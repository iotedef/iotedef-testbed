import argparse
import sys
import os

def result(dname, aname):
    infections = 0
    with open(dname, "r") as f:
        f.readline()
        for line in f:
            if "infection" in line:
                tmp = line.strip().split(", ")
                infections = int(tmp[-1])
                bprecision = float(tmp[3])
                brecall = float(tmp[4])
                bf1 = float(tmp[5])
            if "evolution" in line:
                tmp = line.strip().split(", ")
                eprecision = float(tmp[3])
                erecall = float(tmp[4])
                ef1 = float(tmp[5])
    
    answers = 0
    total = 0
    with open(aname, "r") as f:
        f.readline()
        for line in f:
            total += 1
            tmp = line.strip().split(", ")
            answer = int(tmp[5])

            if answer == 1:
                answers += 1

    print ("Baseline Precision: {}".format(bprecision))
    print ("Baseline Recall: {}".format(brecall))
    print ("Baseline F1: {}".format(bf1))
    print ("Total Infections: {}".format(infections))
    print ("Total Identified Infections: {}".format(total))
    print ("Correct Infections: {}".format(answers))
    print ("Precision: {}".format(round(answers / total, 2)))
    print ("Recall: {}".format(round(answers / infections, 2)))

    try:
        print ("Updated Precision: {}".format(eprecision))
        print ("Updated Recall: {}".format(erecall))
        print ("Updated F1: {}".format(ef1))
    except:
        pass

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--detection", metavar='<detection result file>',
                        help='detection result file', required=True)
    parser.add_argument("-a", "--analysis", metavar='<analysis result file>',
                        help='analysis result file', required=True)
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()

    if not os.path.exists(args.detection):
        print('Input detection file "{}" does not exist'.format(args.detection),
              file=sys.stderr)
        sys.exit(-1)

    if not os.path.exists(args.analysis):
        print('Input analysis file "{}" does not exist'.format(args.analysis),
              file=sys.stderr)
        sys.exit(-1)

    result(args.detection, args.analysis)

if __name__ == '__main__':
    main()
