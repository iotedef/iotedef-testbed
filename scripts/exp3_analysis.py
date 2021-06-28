import argparse
import sys
import os
import math

def average(lst):
    if len(lst) == 0:
        return 0
    return sum(lst)/len(lst)

def stdev(lst):
    squares = []
    for elem in lst:
        squares.append(elem * elem)
    var = average(squares) - average(lst) **2
    return math.sqrt(var)

def f1_score(p, r):
    if p + r == 0:
        return 0
    return round(2 * (p * r) / (p + r), 2)

def analysis(h, c, r, d, m, ofprefix):
    ofname = "{}_individual.csv".format(ofprefix)
    afname = "{}_averaged.csv".format(ofprefix)

    of = open(ofname, "w")
    af = open(afname, "w")

    for a in ["baseline", "attention", "episode_tree", "viterbi"]:

        bprecisions = []
        aprecisions = []
        eprecisions = []

        brecalls = []
        arecalls = []
        erecalls = []

        bf1s = []
        af1s = []
        ef1s = []

        for s in range(1, m+1):
            ids_fprefix = "{}/ids_{}_{}_r{}_d{}".format(h, c, a, r, d)
            ca_fprefix = "{}/ca_{}_{}_r{}_d{}".format(h, c, a, r, d)

            iname = "{}_{}.csv".format(ids_fprefix, s)
            cname = "{}_{}.csv".format(ca_fprefix, s)

            infections = 0
            with open(iname, "r") as f:
                f.readline()
                for line in f:
                    if "infection" in line:
                        tmp = line.strip().split(", ")
                        infections = int(tmp[-1])
                        bprecision = float(tmp[3])
                        brecall = float(tmp[4])
                        bf1 = float(tmp[5])

                        bprecisions.append(bprecision)
                        brecalls.append(brecall)
                        bf1s.append(bf1)

                    if "evolution" in line:
                        tmp = line.strip().split(", ")
                        eprecision = float(tmp[3])
                        erecall = float(tmp[4])
                        ef1 = float(tmp[5])
    
                        eprecisions.append(eprecision)
                        erecalls.append(erecall)
                        ef1s.append(ef1)

            answers = 0
            total = 0
            with open(cname, "r") as f:
                f.readline()
                for line in f:
                    total += 1
                    tmp = line.strip().split(", ")
                    answer = int(tmp[5])

                    if answer == 1:
                        answers += 1

            if total == 0:
                aprecision = 0
            else:
                aprecision = round(answers / total, 2)
            arecall = round(answers / infections, 2)
            af1 = f1_score(aprecision, arecall)

            aprecisions.append(aprecision)
            arecalls.append(arecall)
            af1s.append(af1)

            print (">> ids file: {} <<".format(iname))
            print (">> ca file: {} <<".format(cname))
            print ("Baseline Precision: {}".format(bprecision))
            print ("Baseline Recall: {}".format(brecall))
            print ("Baseline F1: {}".format(bf1))
            print ("Total Infections: {}".format(infections))
            print ("Total Identified Infections: {}".format(total))
            print ("Correct Infections: {}".format(answers))
            print ("Precision: {}".format(aprecision))
            print ("Recall: {}".format(arecall))
            print ("F1: {}".format(af1))
            
            try:
                print ("Updated Precision: {}".format(eprecision))
                print ("Updated Recall: {}".format(erecall))
                print ("Updated F1: {}".format(ef1))
            except:
                pass

            print ("")

            of.write(">> ids file: {} <<\n".format(iname))
            of.write(">> ca file: {} <<\n".format(cname))
            of.write("Baseline Precision: {}\n".format(bprecision))
            of.write("Baseline Recall: {}\n".format(brecall))
            of.write("Baseline F1: {}\n".format(bf1))
            of.write("Total Infections: {}\n".format(infections))
            of.write("Total Identified Infections: {}\n".format(total))
            of.write("Correct Infections: {}\n".format(answers))
            of.write("Precision: {}\n".format(aprecision))
            of.write("Recall: {}\n".format(arecall))
            of.write("F1: {}\n".format(af1))

            try:
                of.write("Updated Precision: {}\n".format(eprecision))
                of.write("Updated Recall: {}\n".format(erecall))
                of.write("Updated F1: {}\n".format(ef1))
            except:
                pass

            of.write("\n")

        print (">> Averaged Result (a: {}) <<".format(a))
        print ("Baseline Precision: {} ({})".format(round(average(bprecisions), 2), round(stdev(bprecisions), 2)))
        print ("Baseline Recall: {} ({})".format(round(average(brecalls), 2), round(stdev(brecalls), 2)))
        print ("Baseline F1: {} ({})".format(round(average(bf1s), 2), round(stdev(bf1s), 2)))
        print ("Precision: {} ({})".format(round(average(aprecisions), 2), round(stdev(aprecisions), 2)))
        print ("Recall: {} ({})".format(round(average(arecalls), 2), round(stdev(arecalls), 2)))
        print ("F1: {} ({})".format(round(average(af1s), 2), round(stdev(af1s), 2)))
        print ("Updated Precision: {} ({})".format(round(average(eprecisions), 2), round(stdev(eprecisions), 2)))
        print ("Updated Recall: {} ({})".format(round(average(erecalls), 2), round(stdev(erecalls), 2)))
        print ("Updated F1: {} ({})".format(round(average(ef1s), 2), round(stdev(ef1s), 2)))
        print ("")

        af.write (">> Averaged Result (a: {}) <<\n".format(a))
        af.write ("Baseline Precision: {} ({})\n".format(round(average(bprecisions), 2), round(stdev(bprecisions), 2)))
        af.write ("Baseline Recall: {} ({})\n".format(round(average(brecalls), 2), round(stdev(brecalls), 2)))
        af.write ("Baseline F1: {} ({})\n".format(round(average(bf1s), 2), round(stdev(bf1s), 2)))
        af.write ("Precision: {} ({})\n".format(round(average(aprecisions), 2), round(stdev(aprecisions), 2)))
        af.write ("Recall: {} ({})\n".format(round(average(arecalls), 2), round(stdev(arecalls), 2)))
        af.write ("F1: {} ({})\n".format(round(average(af1s), 2), round(stdev(af1s), 2)))
        af.write ("Updated Precision: {} ({})\n".format(round(average(eprecisions), 2), round(stdev(eprecisions), 2)))
        af.write ("Updated Recall: {} ({})\n".format(round(average(erecalls), 2), round(stdev(erecalls), 2)))
        af.write ("Updated F1: {} ({})\n".format(round(average(ef1s), 2), round(stdev(ef1s), 2)))
        af.write ("\n")

    of.close()
    af.close()

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-z", "--home", metavar='<home directory of csv files>',
                        help='home directory of csv files', required=True)
    parser.add_argument("-c", "--classifier", metavar='<classifier algorithm used>',
                        help='classifier algorithm used', required=True)
    parser.add_argument("-d", "--dataset", metavar='<dataset number used>',
                        help='dataset number used', required=True)
    parser.add_argument("-r", "--round", metavar='<round value>',
                        help='round value', required=True)
    parser.add_argument("-m", "--maximum", metavar='<maximum serial>',
                        help='maximum serial', required=True, type=int)
    parser.add_argument("-o", "--output", metavar='<output prefix>',
                        help='output file prefix', required=True)
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    analysis(args.home, args.classifier, args.round, args.dataset, args.maximum, args.output)

if __name__ == '__main__':
    main()
