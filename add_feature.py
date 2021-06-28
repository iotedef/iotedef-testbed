import argparse
import sys
import os
from utils.etc import camel_code

def generate_template(ftype, name):
    fname = "features/{}/{}.py".format(ftype, name)

    with open(fname, "w") as f:
        f.write("import sys\n")
        f.write("import logging\n")
        f.write("from features.feature import Feature\n\n")
        f.write("class {}(Feature):\n".format(camel_code(name)))
        f.write("    def __init__(self, name):\n")
        f.write("        super().__init__(name, \"{}\")\n\n".format(ftype))
        f.write("    # Please implement the following function\n")
        f.write("    # The variable `val` should contain the result value\n")
        f.write("    def extract_feature(self, window):\n")
        f.write("        # TODO: Implement the procedure to extract the feature\n")
        f.write("\n")
        f.write("\n")
        f.write("        window.add_feature_value(self.get_name(), val)\n")
        f.write("        logging.debug('{}: {}'.format(self.get_name(), val))\n")

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", required=True, help="Feature type (packet/flow)", type=str)
    parser.add_argument("-n", "--name", required=True, help="Feature name", type=str)
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    ftype = args.type
    name = args.name

    if not (ftype == "packet" or ftype == "flow"):
        print ("Feature type should be either \"packet\" or \"flow\".")
        sys.exit(1)

    fname = "features/{}/{}.py".format(ftype, name)

    if os.path.exists(fname):
        print ("The same name of the feature exists. Please insert another name for the feature to be defined")
        sys.exit(1)

    generate_template(ftype, name)

if __name__ == "__main__":
    main()
