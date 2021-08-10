import os
import sys
import argparse
import logging
from utils.etc import camel_code

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

def make_config(ofname, anames, cnames, enames, pnames, fnames):
    with open(ofname, "w") as of:
        of.write("# Parameters\n")
        of.write("Window Size: 1\n")
        of.write("Sliding Window: True\n")
        of.write("Episode Maximum Length: 100\n")
        of.write("Episode Minimum Frequency: 0.01\n")
        of.write("Episode Minimum Confidence: 0\n")
        of.write("Fixed Length Episode: False\n")
        of.write("Batch Granularity: 0.1\n")
        of.write("Batch Width: 30\n")
        of.write("Classes: B, A, I, R\n")
        of.write("Home Directory: output\n")
        of.write("Round Value: 1\n")
        of.write("IP Address: 127.0.0.1\n")
        of.write("Port: 20000\n")
        of.write("Output Prefix: sequence\n")
        of.write("Analysis Result Prefix: result\n")
        of.write("Number Of Candidates: 10\n")
        of.write("Number Of Results: 10\n")
        of.write("Number Of Final Results: 3\n")
        of.write("Local: False\n")
        of.write("IP Address 0: 10.0.0.69\n")
        of.write("Port 0: 20001\n")
        of.write("IP Address 1: 10.0.60.196\n")
        of.write("Port 1: 20001\n")
        of.write("Self Evolving: False\n")
        of.write("Update Strategy: 1\n")

        of.write("\n# Encoders ({}".format(enames[0]))
        for idx in range(1, len(enames)):
            of.write("/{}".format(enames[idx]))
        of.write(")\n")
        of.write("Encoder: {}\n".format(enames[0]))

        of.write("\n# Algorithms ({}".format(anames[0]))
        for idx in range(1, len(anames)):
            of.write("/{}".format(anames[idx]))
        of.write(")\n")
        of.write("Attack Detection: {}\n".format(anames[3]))
        of.write("Infection Detection: {}\n".format(anames[3]))
        of.write("Reconnaissance Detection: {}\n".format(anames[3]))

        of.write("\n# Causal Analyzer ({}".format(cnames[0]))
        for idx in range(1, len(cnames)):
            of.write("/{}".format(cnames[idx]))
        of.write(")\n")
        of.write("Analyzer: {}\n".format(cnames[1]))
        of.write("\n# Packet Feature Extractors (True/False)\n")
        for f in pnames:
            of.write("{}: True\n".format(f))

        of.write("\n# Flow Feature Extractors (True/False)\n")
        for f in fnames:
            of.write("{}: True\n".format(f))

def make_initializer(anames, cnames, enames, pnames, fnames):
    with open("utils/autils.py", "w") as of:
        of.write("import sys\n")
        of.write("sys.path.append(\"..\")\n")
        
        for f in anames:
            of.write("from algorithms.{} import {}\n".format(f, camel_code(f)))

        of.write("\n")
        of.write("def init_algorithms(model_manager):\n")

        for f in anames:
            of.write("    model_manager.add_algorithm({}(\"{}\"))\n".format(camel_code(f), f))

    with open("utils/cutils.py", "w") as of:
        of.write("import sys\n")
        of.write("sys.path.append(\"..\")\n")
        
        for f in cnames:
            of.write("from analyzers.{} import {}\n".format(f, camel_code(f)))

        of.write("\n")
        of.write("def init_analyzers(causal_analyzer):\n")

        for f in cnames:
            of.write("    causal_analyzer.add_analyzer({}(\"{}\"))\n".format(camel_code(f), f))

    with open("utils/eutils.py", "w") as of:
        of.write("import sys\n")
        of.write("sys.path.append(\"..\")\n")
        
        for f in enames:
            of.write("from encoders.{} import {}\n".format(f, camel_code(f)))

        of.write("\n")
        of.write("def init_encoders(encoder_manager):\n")

        for f in enames:
            of.write("    encoder_manager.add_encoder({}(\"{}\"))\n".format(camel_code(f), f))

    with open("utils/futils.py", "w") as of:
        of.write("import sys\n")
        of.write("sys.path.append(\"..\")\n")
        
        for f in pnames:
            of.write("from features.packet.{} import {}\n".format(f, camel_code(f)))

        for f in fnames:
            of.write("from features.flow.{} import {}\n".format(f, camel_code(f)))

        of.write("\n")
        of.write("def init_features(feature_extractor):\n")
        names = pnames + fnames
        for f in names:
            of.write("    feature_extractor.add_feature({}(\"{}\"))\n".format(camel_code(f), f))

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--algorithms", help="Detection algorithm directory", type=str, default="algorithms")
    parser.add_argument("-c", "--causal", help="Infection identification analyzer directory", type=str, default="analyzers")
    parser.add_argument("-e", "--encoders", help="Encoder directory", type=str, default="encoders")
    parser.add_argument("-f", "--features", help="Feature directory", type=str, default="features")
    parser.add_argument("-o", "--output", help="Output filename", type=str, default="ids_config")
    parser.add_argument("-l", "--log", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", default="INFO", type=str)
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()

    if not os.path.exists(args.algorithms):
        print ("Invalid algorithm directory. Please insert the correct algorithm directory")
        sys.exit(1)

    if not os.path.exists(args.causal):
        print ("Invalid infection identification analyzer directory. Please insert the correct infection identification analyzer directory")
        sys.exit(1)

    if not os.path.exists(args.encoders):
        print ("Invalid encoder directory. Please insert the correct encoder directory")
        sys.exit(1)

    if not os.path.exists(args.features):
        print ("Invalid feature directory. Please insert the correct feature directory")
        sys.exit(1)

    logging.basicConfig(level=args.log)
    anames = prepare_algorithms(args.algorithms)
    cnames = prepare_causal_analyzer(args.causal)
    enames = prepare_encoders(args.encoders)
    pnames, fnames = prepare_features(args.features)

    make_config(args.output, anames, cnames, enames, pnames, fnames)
    make_initializer(anames, cnames, enames, pnames, fnames)

    print ("Please check the feature configure file: {}".format(args.output))

if __name__ == "__main__":
    main()
