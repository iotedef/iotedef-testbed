import argparse
import os
from onehop_encoding import encoded_set, complement

def make_config(anames, cnames, enames, fnames, dname, nexcluding):
    lst = []
    for i in range(nexcluding + 1):
        lst += complement(encoded_set(len(fnames), i))
    lst = sorted(lst)

    num = 0
    for j in range(len(enames)):
        for k in range(len(cnames)):
            for l in lst:
                with open("{}/all_{}".format(dname, num), "w") as of:
                    of.write("# Parameters\n")
                    of.write("Window Size: 1\n")
                    of.write("Sliding Window: True\n")
                    of.write("Episode Period: 0\n")
                    of.write("Episode Output: episodes.csv\n")

                    of.write("\n# Encoders ({}".format(enames[0]))
                    for idx in range(1, len(enames)):
                        of.write("/{}".format(enames[idx]))
                    of.write(")\n")
                    of.write("Encoder: {}\n".format(enames[j]))

                    of.write("\n# Algorithms ({}".format(anames[0]))
                    for idx in range(1, len(anames)):
                        of.write("/{}".format(anames[idx]))
                    of.write(")\n")
                    of.write("Algorithm: {}".format(anames[0]))
                    for i in range(1, len(anames)):
                        of.write(", {}".format(anames[i]))
                    of.write("\n")

                    of.write("\n# Causal Analyzer ({}".format(cnames[0]))
                    for idx in range(1, len(cnames)):
                        of.write("/{}".format(cnames[idx]))
                    of.write(")\n")
                    of.write("Analyzer: {}\n".format(cnames[k]))

                    of.write("\n# Flow Feature Extractors (True/False)\n")
                    for n in range(len(fnames)):
                        if n >= len(l):
                            tf = False
                        elif l[n] == 1:
                            tf = True
                        else:
                            tf = False
                        of.write("{}: {}\n".format(fnames[n], tf))
                num += 1

def prepare_algorithms(dname):
    edir = "{}".format(dname)

    anames = []

    algorithms = [f for f in os.listdir(edir) if f.endswith(".py") and f != "algorithm.py"]

    for a in algorithms:
        anames.append(a.split(".")[0])

    return anames

def prepare_causal_analyzer(dname):
    edir = "{}".format(dname)

    cnames = []

    analyzers = [f for f in os.listdir(edir) if f.endswith(".py") and f != "analyzer.py"]

    for a in analyzers:
        cnames.append(a.split(".")[0])

    return cnames

def prepare_encoders(dname):
    edir = "{}".format(dname)

    enames = []

    encoders = [f for f in os.listdir(edir) if f.endswith(".py") and f != "encoder.py"]

    for e in encoders:
        enames.append(e.split(".")[0])

    return enames

def prepare_features(dname):
    pdir = "{}/packet".format(dname)
    fdir = "{}/flow".format(dname)

    pnames = []
    fnames = []

    pfeatures = [f for f in os.listdir(pdir) if f.endswith(".py")]
    ffeatures = [f for f in os.listdir(fdir) if f.endswith(".py")]

    for f in pfeatures:
        pnames.append(f.split(".")[0])

    for f in ffeatures:
        fnames.append(f.split(".")[0])

    return pnames, fnames

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--algorithms", metavar="<the name of the algorithm directory>", help="Algorithm directory", type=str, default="algorithms")
    parser.add_argument("-c", "--causal", metavar="<the name of the causal analyzer directory>", help="Causal analyzer directory", type=str, default="analyzers")
    parser.add_argument("-d", "--directory", metavar="<the directory where to store configuration files>", help="Directory where to store configuration files", type=str, required=True)
    parser.add_argument("-e", "--encoders", metavar="<the name of the encoder directory>", help="Encoder directory", type=str, default="encoders")
    parser.add_argument("-f", "--features", metavar="<the name of the feature directory>", help="Feature directory", type=str, default="features")
    parser.add_argument("-n", "--number", metavar="<the number of excluded features", help="Number of excluded features", type=int, default=1)
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()

    if not os.path.exists(args.algorithms):
        print ("Invalid algorithm directory. Please insert the correct algorithm directory")
        sys.exit(1)

    if not os.path.exists(args.causal):
        print ("Invalid causal analyzer directory. Please insert the correct causal analyzer directory")
        sys.exit(1)

    if not os.path.exists(args.encoders):
        print ("Invalid encoder directory. Please insert the correct encoder directory")
        sys.exit(1)

    if not os.path.exists(args.features):
        print ("Invalid feature directory. Please insert the correct feature directory")
        sys.exit(1)

    if not os.path.exists(args.directory):
        os.mkdir(args.directory)

    anames = prepare_algorithms(args.algorithms)
    cnames = prepare_causal_analyzer(args.causal)
    enames = prepare_encoders(args.encoders)
    pnames, fnames = prepare_features(args.features)

    make_config(anames, cnames, enames, fnames, args.directory, args.number)

if __name__ == "__main__":
    main()
