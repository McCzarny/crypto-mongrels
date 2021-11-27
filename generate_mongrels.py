#!/usr/local/bin/python3
"""
Generates mongrel json files using the configuration.
"""

import argparse
import random
import os
import json
import sys
import functools
import logging
from math import isclose

def count_possibilities(config):
    """
    Counts how many unique mongrels could be generated using the configuration.
    """
    total_variations = 0
    for kind in config['kinds']:
        features_variations = 1
        for feature in kind['features']:
            features_variations *= len(feature['variants'])
        features_variations *= len(kind['color schemes'])
        total_variations += features_variations
        logging.info("Total possible variants for kind: %i", features_variations)
    return total_variations

def validate_configuration(config):
    """
    Checks if the configuration is valid.
    Calculates if all possibilities sums up to 1.0.
    """
    total_kinds= functools.reduce(lambda x,y:x+float(y['probability']), config['kinds'],0)
    logging.debug("Total probabilities for all kinds is %d", total_kinds)

    assert isclose(total_kinds, 1.0),\
    f"The sum of probabilities for all kinds must be equal to 1 (is {total_kinds})."

    for kind in config['kinds']:
        for feature in kind['features']:
            total_features = \
                functools.reduce(lambda x,y:x+float(y['probability']), feature['variants'],0)
            logging.debug("Total probabilities for \"%s\" is %d", feature['name'], total_features)
            assert isclose(total_features, 1.0), \
                f"Sum of probabilities for feature \"{feature['name']}\" != 1 ({total_features})."

def load_configuration(file):
    """
    Loads the configuration json file.
    """
    configuration = json.load(file)
    validate_configuration(configuration)
    logging.info("Total possible variants: %i", count_possibilities(configuration))
    return configuration

def generate_id(objects_with_probabilities, rng):
    """
    Generates a semirandom ID using the probabilities defined in the configuration.
    """
    random_number = rng.uniform(0,1)
    for idx, objects_with_probability in enumerate(objects_with_probabilities):
        random_number -= objects_with_probability['probability']
        if random_number <= 0.0:
            return idx

    assert False, "Reached unreachable code."

def get_relative_path_to_mongrel_schema(file_directory):
    """
    Returns relative path to the mongrel schema file.
    """
    schame_directory = os.path.join(sys.path[0], "mongrel.schema.json")
    return os.path.relpath(schame_directory, file_directory)


def generate_morgel(seed, output_file, configuration):
    """
    Generates a single mongrel using the configuration.
    """
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

    logging.debug("Generated mongrel: %s", mongrel)

    with open(output_file, 'w', encoding = 'utf-8') as file:
        json.dump(mongrel, file, indent=4)

def generate(configuration, output, count, seeds, override):
    """
    Generates mongrels.
    """
    for current_id in range(count):
        print (f"ID: {current_id}, seed: {seeds[current_id]}")
        output_file = os.path.join(output,f"{current_id}.json")
        if os.path.isfile(output_file) and not override:
            logging.info("Skipping %s as the file already exists.", output_file)
            continue
        generate_morgel(seeds[current_id], output_file, configuration)


parser =\
    argparse.ArgumentParser(description='Generate mongrels using a configuration file and a seed.')
parser.add_argument('--configuration', type=str, nargs='?',
                    help='a path to the configuration file', default="configuration.json")
parser.add_argument('--seed', type=int, nargs='?',
                    help='a seed for RNG', default=0)
parser.add_argument('--count', type=int, nargs='?',
                    help='number of dogs to generate', default=50)
parser.add_argument('--output', type=str, nargs='?',
                    help='Output directory', default="mongrels")
parser.add_argument('--logfile', type=str, nargs='?',
                    help='Logs file', default="log.txt")
parser.add_argument('--override', type=bool, nargs='?',
                    help='Override generated mongrels', default=True)

args = parser.parse_args()

print(args)

logging.basicConfig(filename=args.logfile, encoding='utf-8', level=logging.DEBUG)
random.seed(args.seed)
output_dir = os.path.join(sys.path[0],args.output)

if not os.path.exists(output_dir):
    logging.info("Creating the output directory %s", output_dir)
    os.makedirs(output_dir)

with open(args.configuration, encoding='UTF8') as configuration_file:
    configuration_json = load_configuration(configuration_file)
    generated_seeds = [random.random() for _ in range(args.count)]
    generate(configuration_json, output_dir, args.count, generated_seeds, args.override)
