#!/usr/local/bin/python3
"""
Checks if there is any duplicate mongrels.
"""

import os
import sys
import json


class HashableDict(dict):
    """
    Class that allows to store a dictionary in a hashtable.
    """
    def __hash__(self):
        return hash(frozenset(self))

directory_path = os.path.join(
    sys.path[0], "./mongrels") if len(sys.argv) < 2 else sys.argv[1]

mongrels = {}

for mongrel_file in os.listdir(directory_path):
    if mongrel_file.endswith("json"):
        full_path = os.path.join(directory_path, mongrel_file)
        with json.load(open(full_path, encoding="utf-8")) as mongrel:
            mongrel_key = HashableDict(mongrel)
            if not mongrels.get(mongrel_key):
                mongrels[mongrel_key] = mongrel_file
            else:
                print(f"{mongrel_file} duplicates {mongrels[mongrel_key]}")
