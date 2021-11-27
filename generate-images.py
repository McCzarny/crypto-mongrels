#!/usr/local/bin/python3

import argparse, json, os, PIL, sys
from PIL import Image, ImageColor

def read_image(path):
    try:
        image = PIL.Image.open(path, 'r')
        return image
    except Exception as e:
        print(e)

def add_layer(feature_configuration, freature_id, destination):
    image_path = feature_configuration['variants'][freature_id]['image']
    overlay = read_image(os.path.join(sys.path[0],image_path))
    destination.paste(overlay, (0, 0), overlay)

def apply_color_scheme(image, default_colors, destination_colors):
    if default_colors == destination_colors:
        return

    input_data = image.getdata()
    output_data = []

    for item in input_data:
        try:
            index = default_colors.index(item[:-1])
            destination_color = destination_colors[index]
            destination_color = destination_color + (item[3],)
            output_data.append(destination_color) 
        except ValueError:
            output_data.append(item)

    image.putdata(output_data)

def get_color_scheme(configuration):
    color_scheme = []
    for hex_color in configuration:
        color_scheme.append(ImageColor.getcolor(hex_color, "RGB"))
    return color_scheme

def generate_image(mongrel, configuration, destination):
    kind_id = mongrel["kind"]
    kind = configuration['kinds'][kind_id]
    default_image  = kind['default image']
    print(default_image)
    image = read_image(os.path.join(sys.path[0],default_image))

    for idx, feature in enumerate(kind['features']):
        add_layer(feature, mongrel['features'][idx], image)
    default_color_scheme = get_color_scheme(kind['default color scheme'])
    destination_color_scheme = get_color_scheme(kind['color schemes'][mongrel['color scheme']]['colors'])
    apply_color_scheme(image, default_color_scheme, destination_color_scheme)
    #image.show()
    image.save(destination, "PNG")

parser = argparse.ArgumentParser(description='Generate mongrels using a configuration file and a seed.')
parser.add_argument('configuration', type=str, nargs='?',
                    help='a path to the configuration file', default="configuration.json")
parser.add_argument('output', type=str, nargs='?',
                    help='Output directory', default="images")
parser.add_argument('input', type=str, nargs='?',
                    help='Input directory', default="mongrels")

args = parser.parse_args()

print(args)

configuration = json.load(open(args.configuration))

output_dir = os.path.join(sys.path[0], args.output)  
if (not os.path.exists(output_dir)):
    print(f"Creating the output directory {output_dir}")
    os.makedirs(output_dir)

for mongrel_file in os.listdir(args.input):
    if mongrel_file.endswith("json"):
        mongrel = json.load(open(os.path.join(args.input, mongrel_file)))
        destination_file = os.path.join(output_dir, mongrel_file.replace("json", "png"))
        generate_image(mongrel, configuration, destination_file)