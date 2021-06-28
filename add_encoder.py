import argparse
import sys
import os
from utils.etc import camel_code

def generate_template(name):
    fname = "encoders/{}.py".format(name)

    with open(fname, "w") as f:
        f.write("import sys\n")
        f.write("import logging\n")
        f.write("from encoders.encoder import Encoder\n\n")
        f.write("class {}(Encoder):\n".format(camel_code(name)))
        f.write("    def __init__(self, name):\n")
        f.write("        super().__init__(name)\n\n")
        f.write("    # Please implement the following function\n")
        f.write("    def encoding(self, window):\n")
        f.write("        logging.debug('{}'.format(self.get_name()))\n")

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", required=True, help="Encoder name", type=str)
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    name = args.name

    fname = "encoders/{}.py".format(name)

    if os.path.exists(fname):
        print ("The same name of the encoder exists. Please insert another name for the encoder to be defined")
        sys.exit(1)

    generate_template(name)

if __name__ == "__main__":
    main()
