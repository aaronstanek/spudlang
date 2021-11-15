# the main file of the program

import sys
import os
from .SpudLoader import SpudLoader
from .Rule import RuleBox

def main():
    if len(sys.argv) != 2:
        raise Exception("Expected a file to process")
    if os.path.isabs(sys.argv[1]):
        initial_path = sys.argv[1]
    else:
        initial_path = os.path.join(os.getcwd(),sys.argv[1])
    loader = SpudLoader()
    loader.recursive_load_parse(initial_path,True)
    rulebox = RuleBox()
    rulebox.add(loader.rules)
    html = rulebox.resolve_to_html_document(loader.ingredients)
    with open("ResultsTree.html","w") as file:
        file.write(html)

if __name__ == "__main__":
    main()