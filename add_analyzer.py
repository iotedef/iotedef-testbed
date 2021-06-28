import argparse
import sys
import os
from utils.etc import camel_code

def generate_template(name):
    fname = "analyzers/{}.py".format(name)

    with open(fname, "w") as f:
        f.write("import sys\n")
        f.write("import logging\n")
        f.write("from analyzers.analyzer import Analyzer\n\n")
        f.write("class {}(Analyzer):\n".format(camel_code(name)))
        f.write("    def __init__(self, name):\n")
        f.write("        super().__init__(name)\n\n")
        f.write("    # Please implement the following functions\n")
        f.write("    def learning(self, sequence, config):\n")
        f.write("        logging.debug('Learning: {}'.format(self.get_name()))\n\n")
        f.write("    def analysis(self, sequence, config):\n")
        f.write("        logging.debug('Analysis: {}'.format(self.get_name()))\n\n")

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", required=True, help="Analyzer name", type=str)
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    name = args.name

    fname = "analyzer/{}.py".format(name)

    if os.path.exists(fname):
        print ("The same name of the analyzer exists. Please insert another name for the analyzer to be defined")
        sys.exit(1)

    generate_template(name)

if __name__ == "__main__":
    main()
