import argparse
import time
import logging
import socket
import threading
import os
import asyncio
import sys
from utils.eutils import init_encoders
from definitions.sequence import Sequence
from definitions.states import State
from utils.cutils import init_analyzers

usleep = lambda x: time.sleep(x/1000000.0)
THREAD_USLEEP_TIME=1000
PROCESS_TIMEOUT=3/1000000.0

MAX_SIZE = 100
THRESHOLD = 10
BUF_SIZE = 256

class CausalAnalyzer:
    def __init__(self, conf, ofname=None, serial=None, trname=None, tename=None):
        self.config = parse_config(conf, serial)
        if ofname and serial:
            self.config["output"] = "ca_{}_{}.csv".format(ofname, serial)
        elif ofname:
            self.config["output"] = "{}.csv".format(ofname)
        self.sequence = []
        self.infection_labeled_states = []
        self.analyzers = {}
        init_analyzers(self)
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sock.bind((self.config["ipaddr"], self.config["port"]))
        self.client = None
        self.evolve = False
        self.training = trname
        self.testing = tename

        loop = asyncio.new_event_loop()
        ca = threading.Thread(target=run, args=(self, loop,))
        ca.start()

    def add_analyzer(self, analyzer):
        self.analyzers[analyzer.get_name()] = analyzer
        logging.debug("Analyzer {} is loaded".format(analyzer.get_name()))

    def generate_sequence(self, sfname, training):
        states = []
        with open(sfname, "r") as f:
            fnames = f.readline().split(": ")[0].split(", ")
            num = 0

            for line in f:
                num += 1
                flow, v, s, ts, al, il, rl, ald, ild, rld, bp, ap, ip, rp = line.strip().split(": ")
                vs = v.split(", ")
                values = []
                for val in vs:
                    values.append(float(val))

                start_time, end_time = ts.split(", ")
                start_time = round(float(start_time), self.config["rv"])
                end_time = round(float(end_time), self.config["rv"])
                serial = int(s)
                logging.debug("{} > start_time: {}, end_time: {}".format(num, start_time, end_time))
                labels = {}
                labels["attack"] = int(al)
                labels["infection"] = int(il)
                labels["reconnaissance"] = int(rl)

                labeled = {}
                labeled["attack"] = int(ald)
                labeled["infection"] = int(ild)
                labeled["reconnaissance"] = int(rld)

                probability = {}
                probability["benign"] = float(bp)
                probability["attack"] = float(ap)
                probability["infection"] = float(ip)
                probability["reconnaissance"] = float(rp)
                state = State(serial, flow.replace("/", ":"), fnames, values, labels, labeled, probability, start_time, end_time, training)
                states.append(state)

                if not training:
                    if state.get_labeled("infection") == 1:
                        self.infection_labeled_states.append(state)

        start_time = round(states[0].get_start_time(), self.config["rv"])
        end_time = round(states[-1].get_end_time(), self.config["rv"])
        sequence = Sequence(states, start_time, end_time, self.config["granularity"], self.config["width"])

        if not training:
            logging.info("Sequence is generated: length: {}".format(sequence.get_sequence_length()))
        return sequence

    def process_episodes(self):
        for e in self.episodes:
            if e.get_num_of_windows() >= MAX_SIZE:
                cnt = 0
                label = 0
                labeled = 0
                tp = 0
                tn = 0
                fp = 0
                fn = 0

                for w in e.get_windows():
                    cnt += 1
                    if w.get_label("attack") == 1:
                        label += 1
                    if w.get_labeled("attack") == 1:
                        labeled += 1

                    if w.get_label("attack") == 0 and w.get_labeled("attack") == 0:
                        tn += 1
                    elif w.get_label("attack") == 0 and w.get_labeled("attack") == 1:
                        fp += 1
                    elif w.get_label("attack") == 1 and w.get_labeled("attack") == 0:
                        fn += 1
                    elif w.get_label("attack") == 1 and w.get_labeled("attack") == 1:
                        tp += 1
                
                if label >= THRESHOLD and labeled >= THRESHOLD:
                    logging.debug("Episode ({}): Correctly Classifed as Malicious (Should be Malicious)".format(e.get_algo_name()))
                elif label >= THRESHOLD and labeled < THRESHOLD:
                    logging.debug("Episode ({}): Incorrectly Classified as Benign (Should be Malicious)".format(e.get_algo_name()))
                elif label < THRESHOLD and labeled >= THRESHOLD:
                    logging.debug("Episode ({}): Incorrectly Classified as Malicious (Should be Benign)".format(e.get_algo_name()))
                elif label < THRESHOLD and labeled < THRESHOLD:
                    logging.debug("Episode ({}): Correctly Classified as Benign (Should be Benign)".format(e.get_algo_name()))

                logging.debug("  - Total: {}".format(cnt))
                logging.debug("  - Threshold: {}".format(THRESHOLD))
                logging.debug("  - True Positive: {}".format(tp))
                logging.debug("  - True Negative: {}".format(tn))
                logging.debug("  - False Positive: {}".format(fp))
                logging.debug("  - False Negative: {}".format(fn))
                logging.debug("\n")
                
                if self.output:
                    with open(self.output, "a") as of:
                        of.write("{}, {}, {}, {}, {}, {}, {}, {}, {}\n".format(e.get_algo_name(), e.get_serial_number(), label >= THRESHOLD, labeled >= THRESHOLD, cnt, tp, tn, fp, fn))
                self.episodes.remove(e)

async def main_loop(ca):
    sock = ca.sock

    if ca.training and ca.testing:
        anames = ca.config["cnames"]
        logging.debug("analyzers: {}".format(anames))
        logging.info("ca.training: {}".format(ca.training))
        await process_operation(ca, "training", ca.training, anames, False)
        logging.info("ca.testing: {}".format(ca.testing))
        await process_operation(ca, "test", ca.testing, anames, False)
    else:
        while True:
            pair = sock.recvfrom(BUF_SIZE)
            msg = pair[0].decode()
            ca.client = pair[1]
            op, algs, fname = msg.split(":")
            fname = fname.strip()

            anames = algs.split(",")
            rlst = []
            for aname in anames:
                if aname not in ca.analyzers:
                    rlst.append(aname)

            for rname in rlst:
                logging.error("No corresponding algorithm {} is exist".format(rname))
                anames.remove(rname)

            if op == "evolve":
                ca.evolve = True
                op = "test"

            await process_operation(ca, op, fname, anames, True)

async def process_operation(ca, op, fname, anames, dynamic):
    if op == "training":
        logging.info("Operation: training, Algorithms: {}, File: {}".format(anames, fname))
        sequence = ca.generate_sequence(fname, True)
        #sequence.print_sequence()
        for aname in anames:
            ca.analyzers[aname].learning(sequence, ca.config)
        if dynamic:
            os.remove(fname)

    elif op == "test":
        sequence = ca.generate_sequence(fname, False)
        #sequence.print_sequence()
        logging.info("Operation: test, Algorithms: {}, File: {}".format(anames, fname))

        for aname in anames:
            while not ca.analyzers[aname].model_exists():
                time.sleep(10)
            infections = ca.analyzers[aname].analysis(sequence, ca.config)
        if dynamic:
            os.remove(fname)

        candidates = ca.infection_labeled_states
        serials = []
        if infections:
            for state1 in candidates:
                for _, state2 in infections:
                    if state1.get_serial_number() == state2.get_serial_number():
                        serials.append(state1.get_serial_number())
                        break

        msg = "update:"
        if len(serials) > 0:
            for serial in serials[:-1]:
                msg += "{},".format(serial)
            msg += str(serials[-1])

        logging.debug("msg: {}".format(msg))
        if dynamic:
            ca.sock.sendto(str.encode(msg), ca.client)
        else:
            logging.info("msg: {}".format(msg))

        logging.info("Quit the Causal Analyzer")
        sys.exit(0)

def run(ca, loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_loop(ca))

def parse_config(conf, serial):
    info = {}
    features = {}
    states = {}

    with open(conf, "r") as f:
        for line in f:
            try:
                line = line.strip()
                if line.startswith("#"):
                    continue
                if line == "":
                    continue

                key, val = line.split(":")
                key = key.strip()
                val = val.strip()

                if key == "Window Size":
                    wsize = float(val)
                    info["wsize"] = wsize
                elif key == "Sliding Window":
                    if val.lower() == "true":
                        swnd = True
                    elif val.lower() == "false":
                        swnd = False
                    else:
                        swnd = None
                    info["sliding_window"] = swnd
                elif key == "Episode Maximum Length":
                    max_len = int(val)
                    info["max_len"] = max_len
                elif key == "Episode Minimum Frequency":
                    min_fr = float(val)
                    info["min_fr"] = min_fr
                elif key == "Episode Minimum Confidence":
                    min_conf = float(val)
                    info["min_conf"] = min_conf
                elif key == "Fixed Length Episode":
                    if "True" in val:
                        fixed = True
                    else:
                        fixed = False
                    info["fixed"] = fixed
                elif key == "Batch Granularity":
                    granularity = float(val)
                    info["granularity"] = granularity
                elif key == "Batch Width":
                    width = float(val)
                    info["width"] = width
                elif key == "Classes":
                    lst = val.split(", ")
                    for i in range(len(lst)):
                        states[i] = lst[i]
                    info["classes"] = states
                elif key == "Home Directory":
                    home = val
                    home = os.path.abspath(home)
                    if not os.path.exists(home):
                        os.mkdir(home)
                    info["home"] = home
                elif key == "Round Value":
                    rv = int(val)
                    info["rv"] = rv
                elif key == "IP Address":
                    ipaddr = val
                    info["ipaddr"] = ipaddr
                elif key == "Port":
                    port = int(val)
                    info["port"] = port
                elif key == "Output Prefix":
                    ofprefix = val
                    info["ofprefix"] = ofprefix
                elif key == "Analysis Result Prefix":
                    afprefix = val
                    info["output"] = "{}_{}.csv".format(afprefix, serial)
                elif key == "Number Of Candidates":
                    nresults = val
                    info["ncandidates"] = int(val)
                elif key == "Number Of Results":
                    nresults = val
                    info["nresults"] = int(val)
                elif key == "Number Of Final Results":
                    nresults = val
                    info["nfinal"] = int(val)
                elif key == "Local":
                    if "True" in val:
                        local = True
                    else:
                        local = False
                    info["local"] = local
                elif key == "IP Address 0":
                    info["ipaddr0"] = val
                elif key == "Port 0":
                    info["port0"] = int(val)
                elif key == "IP Address 1":
                    info["ipaddr1"] = val
                elif key == "Port 1":
                    info["port1"] = int(val)
                elif key == "Episode Output":
                    efname = val
                    info["efname"] = efname
                elif key == "Update Strategy":
                    info["strategy"] = val
                elif key == "Encoder":
                    ename = val
                    info["encoder"] = ename
                elif key == "Attack Detection":
                    anames = val.split(",")
                    for i in range(len(anames)):
                        anames[i] = anames[i].strip()
                    info["anames"] = anames
                elif key == "Infection Detection":
                    inames = val.split(",")
                    for i in range(len(inames)):
                        inames[i] = inames[i].strip()
                    info["inames"] = inames
                elif key == "Reconnaissance Detection":
                    rnames = val.split(",")
                    for i in range(len(rnames)):
                        rnames[i] = rnames[i].strip()
                    info["rnames"] = rnames
                elif key == "Analyzer":
                    cnames = val.split(",")
                    for i in range(len(cnames)):
                        cnames[i] = cnames[i].strip()
                    info["cnames"] = cnames
                else:
                    if val.lower() == "true":
                        tf = True
                    elif val.lower() == "false":
                        tf = False
                    else:
                        continue
                    features[key] = tf
                    info["features"] = features
            except:
                logging.error("Error in parsing the line: {}".format(line))
                continue
    return info

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", required=True, help="Configuration file", metavar="<configuration file>", type=str)
    parser.add_argument("-l", "--log", metavar="<log level>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str)
    parser.add_argument("-i", "--training", metavar="<input training sequence file>", help="Input File Name (training)", type=str)
    parser.add_argument("-j", "--testing", metavar="<input testing sequence file>", help="Input File Name (testing)", type=str)
    parser.add_argument("-o", "--output", metavar="<output file name prefix>", help="Output File Name Prefix", type=str, default=None)
    parser.add_argument("-s", "--serial", help="Serial number to correlate the result file of the IDS and the causal analyzer", metavar="<serial number>", type=int, default=None)

    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    causal_analyzer = CausalAnalyzer(args.config, args.output, args.serial, trname=args.training, tename=args.testing)

if __name__ == "__main__":
    main()
