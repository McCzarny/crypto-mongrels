#!/usr/local/bin/python3
"""Uses mongrel json files to generate images """

import argparse
import json
import os
import sys
import PIL
from PIL import Image

def read_image(path):
    """
    Reads an image file and returns it.
    """
    try:
        image = Image.open(path, 'r')
        return image
    except (FileNotFoundError, PIL.UnidentifiedImageError, ValueError, TypeError)  as exception:
        print(exception)
        return None

def add_layer(feature_configuration, freature_id, destination):
    """
    Applies a new layer to the existing image.
    """
    image_path = feature_configuration['variants'][freature_id]['image']
    overlay = read_image(os.path.join(sys.path[0],image_path))
    destination.paste(overlay, (0, 0), overlay)

def apply_color_scheme(image, default_colors, destination_colors):
    """
    Applies a new color scheme to the image.
    """
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

def get_color_scheme(color_configuration):
    """
    Generates an array with colors according to a configuration.
    """
    color_scheme = []
    for hex_color in color_configuration:
        color_scheme.append(PIL.ImageColor.getcolor(hex_color, "RGB"))
    return color_scheme

def generate_image(mongrel, configuration, destination):
    """
    Generates an image based on a configuration.
    """
    kind_id = mongrel["kind"]
    kind = configuration['kinds'][kind_id]
    default_image  = kind['default image']
    print(default_image)
    image = read_image(os.path.join(sys.path[0],default_image))

    for idx, feature in enumerate(kind['features']):
        add_layer(feature, mongrel['features'][idx], image)
    default_color_scheme = get_color_scheme(kind['default color scheme'])
    color_scheme_id = mongrel['color scheme']
    destination_color_scheme = get_color_scheme(kind['color schemes'][color_scheme_id]['colors'])
    apply_color_scheme(image, default_color_scheme, destination_color_scheme)
    #image.show()
    image.save(destination, "PNG")

DESCRIPTION = "Generate mongrels using a configuration file and a seed."
parser = argparse.ArgumentParser(description=DESCRIPTION)
parser.add_argument('configuration', type=str, nargs='?',
                    help='a path to the configuration file', default="configuration.json")
parser.add_argument('output', type=str, nargs='?',
                    help='Output directory', default="images")
parser.add_argument('input', type=str, nargs='?',
                    help='Input directory', default="mongrels")

args = parser.parse_args()

print(args)

with open(args.configuration, encoding='utf-8') as configuration_file:
    configuration_json = json.load(configuration_file)
    output_dir = os.path.join(sys.path[0], args.output)
    if not os.path.exists(output_dir):
        print(f"Creating the output directory {output_dir}")
        os.makedirs(output_dir)

    for mongrel_file_name in os.listdir(args.input):
        if mongrel_file_name.endswith("json"):
            full_path = os.path.join(args.input, mongrel_file_name)
            with open(full_path, encoding='utf-8') as mongrel_file:
                mongrel_json = json.load(mongrel_file)
                destination_file =\
                    os.path.join(output_dir, mongrel_file_name.replace("json", "png"))
                generate_image(mongrel_json, configuration_json, destination_file)
