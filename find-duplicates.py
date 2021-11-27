#!/usr/local/bin/python3

import os, sys, json

class hashabledict(dict):
    def __hash__(self):
        return hash(frozenset(self))

directory_path =  os.path.join(sys.path[0],"./mongrels") if len(sys.argv) < 2 else sys.argv[1]

mongrels = {}

for mongrel_file in os.listdir(directory_path):
    if mongrel_file.endswith("json"):
        mongrel = json.load(open(os.path.join(directory_path, mongrel_file)))
        mongrel_key = hashabledict(mongrel)
        if not mongrels.get(mongrel_key):
            mongrels[mongrel_key] = mongrel_file
        else:
            print(f"{mongrel_file} duplicates {mongrels[mongrel_key]}")
