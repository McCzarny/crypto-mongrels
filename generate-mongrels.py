#!/usr/local/bin/python3

import argparse, random, os, json, sys, functools, logging
from math import isclose

def count_possibilities(config):
    total_variations = 0
    for kind in config['kinds']:
        features_variations = 1
        for feature in kind['features']:
            features_variations *= len(feature['variants'])
        features_variations *= len(kind['color schemes'])
        total_variations += features_variations
        logging.info(f"Total possible variants for kind: {features_variations}")
    return total_variations

def validate_configuration(config):
    total_kinds= functools.reduce(lambda x,y:x+float(y['probability']), config['kinds'],0)
    logging.debug(f"Total probabilities for all kinds is {total_kinds}")
    assert isclose(total_kinds, 1.0), f"The sum of probabilities for all kinds must be equal to 1 (is {total_kinds})."

    for kind in config['kinds']:
        for feature in kind['features']:
            total_features = functools.reduce(lambda x,y:x+float(y['probability']), feature['variants'],0)
            logging.debug(f"Total probabilities for \"{feature['name']}\" is {total_features}")
            assert isclose(total_features, 1.0), f"The sum of probabilities for a feature \"{feature['name']}\" must be equal to 1 (is {total_features})."

def load_configuration(file):
    configuration = json.load(file)
    print (configuration)
    validate_configuration(configuration)
    logging.info(f"Total possible variants: {count_possibilities(configuration)}")
    return configuration

def generate_id(objects_with_probabilities, rng):
    random_number = random.uniform(0,1)
    for idx, objects_with_probability in enumerate(objects_with_probabilities):
        random_number -= objects_with_probability['probability']
        if random_number <= 0.0:
            return idx

    assert False, "Reached unreachable code."

def get_relative_path_to_mongrel_schema(file_directory):
    schame_directory = os.path.join(sys.path[0], "mongrel.schema.json")
    return os.path.relpath(schame_directory, file_directory)


def generate_morgel(seed, output_file):
    rng = random.Random(seed)
    mongrel = {}
    #schema
    mongrel['@schema'] = get_relative_path_to_mongrel_schema(os.path.dirname(output_file))
    mongrel['seed'] = str(seed)
    #kind
    kind_id = generate_id(configuration['kinds'], rng)
    mongrel['kind'] = kind_id
    #features
    features = []
    for feature in configuration['kinds'][kind_id]['features']:
        features.append(generate_id(feature['variants'], rng))
    mongrel['features'] = features
    #color scheme
    mongrel['color scheme'] = generate_id(configuration['kinds'][kind_id]['color schemes'], rng)

    logging.debug(f"Generated mongrel: {mongrel}")

    with open(output_file, 'w') as f:
        json.dump(mongrel, f, indent=4)

def generate(configuration, output, count, seeds, override):
    for id in range(count):
        print (f"ID: {id}, seed: {seeds[id]}")
        output_file = os.path.join(output,f"{id}.json")
        if os.path.isfile(output_file) and not override:
            logging.info(f"Skipping {output_file} as the file already exists.")
            continue
        generate_morgel(seeds[id], output_file)


parser = argparse.ArgumentParser(description='Generate mongrels using a configuration file and a seed.')
parser.add_argument('configuration', type=str, nargs='?',
                    help='a path to the configuration file', default="configuration.json")
parser.add_argument('seed', type=int, nargs='?',
                    help='a seed for RNG', default=0)
parser.add_argument('count', type=int, nargs='?',
                    help='number of dogs to generate', default=50)
parser.add_argument('output', type=str, nargs='?',
                    help='Output directory', default="mongrels")
parser.add_argument('logfile', type=str, nargs='?',
                    help='Logs file', default="log.txt")
parser.add_argument('override', type=bool, nargs='?',
                    help='Override generated mongrels', default=True)

args = parser.parse_args()

print(args)

logging.basicConfig(filename=args.logfile, encoding='utf-8', level=logging.DEBUG)
random.seed(args.seed)
output_dir = os.path.join(sys.path[0],args.output)

if (not os.path.exists(output_dir)):
    logging.info(f"Creating the output directory {output_dir}")
    os.makedirs(output_dir)

configuration = load_configuration(open(args.configuration))
seeds = [random.random() for _ in range(args.count)]
generate(configuration, output_dir, args.count, seeds, args.override)
