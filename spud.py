# the main file of the program

import sys
import os
import hashlib
import Parse

def load_file_raw(path):
    if path[-5:] != ".spud":
        path = path + ".spud"
    if os.path.isfile(path):
        with open(path,"rb") as file:
            return file.read()
    else:
        raise Exception("Unable to locate file: "+path)

def convert_to_absolute_pathnames(base,path):
    if os.path.isabs(path):
        return path
    

def recursive_load(path,seen=set()):
    # recursively loads all input files
    raw_data = load_file_raw(path)
    hex_hash = hashlib.sha256(raw_data).hexdigest()
    if hex_hash in seen:
        # we have already loaded this file
        return []
    else:
        # hex_hash has not been seen yet
        seen.add(hex_hash)
    raw_data = Parse.convert_equivalent_codes(raw_data)
    raw_data = Parse.make_lines(raw_data)
    raw_data = list(filter(lambda x: not Parse.is_empty(x), raw_data))
    raw_data = list(filter(lambda x: not Parse.is_comment(x), raw_data))
    # raw_data is now a list of strings
    # there are no empty lines
    # and no comments
    imports = list(filter(lambda x: Parse.is_import(x), raw_data))
    imports = list(map(lambda x: Parse.interpret_import(x), imports))
    output = []
    for import_path in imports:
        if not os.path.isabs(import_path):
            import_path = os.path.join(os.path.dirname(path),import_path)
            import_path = os.path.abspath(import_path)
        output += recursive_load(import_path,seen)
    raw_data = list(filter(lambda x: not Parse.is_import(x), raw_data))
    output += raw_data
    return output

def main():
    if len(sys.argv) != 2:
        raise Exception("Expected a file to process")
    if os.path.isabs(sys.argv[1]):
        initial_path = sys.argv[1]
    else:
        initial_path = os.path.join(os.getcwd(),sys.argv[1])
    lines = recursive_load(initial_path)
    # lines are the all the lines of the input
    # in order, as strings
    # no comments, imports or empty lines
    lines = list(map(lambda x: Parse.validate_and_expand(x), lines))
    lines = list(map(lambda x: Parse.make_words(x), lines))
    print(lines)

if __name__ == "__main__":
    main()