import argparse
import os
import logging
import subprocess
import time
import threading
import sys
import asyncio
import signal
import socket
from modules.packet_capturer import PacketCapturer
from modules.window_manager import WindowManager
from modules.feature_extractor import FeatureExtractor
from modules.encoding_manager import EncodingManager
from modules.model_manager import ModelManager
from modules.sequence_manager import SequenceManager

usleep = lambda x: time.sleep(x/1000000.0)
BUF_SIZE = 16384
THREAD_USLEEP_TIME=1000000
OFFSET = 3

class IDSCore:
    def __init__(self, conf, sidx, ofname, serial=None, evolve=-1):
        tsname = "../dataset/set_{}/training.pcap".format(sidx)
        tiname = "../dataset/set_{}/training.info".format(sidx)

        esname = "../dataset/set_{}/test.pcap".format(sidx)
        einame = "../dataset/set_{}/test.info".format(sidx)

        rsname = None
        riname = None
        if evolve > 0:
            rsname = "../dataset/set_{}/test.pcap".format(evolve)
            riname = "../dataset/set_{}/test.info".format(evolve)

        if not os.path.exists(tsname):
            logging.error("No Training Set exists")
            sys.exit(1)

        if not os.path.exists(tiname):
            logging.error("No Training Set Information file exists")
            sys.exit(1)

        if not os.path.exists(esname):
            logging.error("No Test Set exists")
            sys.exit(1)

        if not os.path.exists(einame):
            logging.error("No Test Set Information file exists")
            sys.exit(1)

        if rsname and not os.path.exists(rsname):
            logging.error("No Test Set exists: {}".format(rsname))
            sys.exit(1)

        if riname and not os.path.exists(riname):
            logging.error("No Test Set Information file exists")
            sys.exit(1)

        if serial:
            self.output = "ids_{}_{}.csv".format(ofname, serial)
        else:
            self.output = "{}.csv".format(ofname)
        self.conf = conf
        self.sidx = sidx
        self.eidx = evolve

        self.is_training = False
        self.tcpreplay_start_for_training = False
        self.tcpreplay_end_for_training = False
        self.is_testing = False

        self.tcpreplay_start_for_testing = False
        self.tcpreplay_end_for_testing = False
        self.is_training_set_processed = False
        self.is_test_set_processed = False

        self.is_retesting = False
        self.tcpreplay_start_for_retesting = False
        self.tcpreplay_end_for_retesting = False
        self.is_retest_set_processed = False

        self.training_set_name = tsname
        self.training_set_info = parse_info(tiname)
        self.test_set_name = esname
        self.test_set_info = parse_info(einame)
        self.retest_set_name = rsname
        if riname:
            self.retest_set_info = parse_info(riname)
        else:
            self.retest_set_info = None

        self.training_start_time = None
        self.test_start_time = None
        self.retest_start_time = None
        self.attack_start_time = None
        self.infection_start_time = None
        self.reconnaissance_start_time = None
        self.attack_end_time = None
        self.packet_capturer = None
        self.window_manager = None
        self.feature_extractor = None
        self.encoding_manager = None
        self.sequence_manager = None
        self.model_manager = None
        self.causal_analyzer = None

        self.model_is_generated = False

        self.local = False
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.ipaddr = {}
        self.ports = {}

        if evolve > 0:
            self.evolve = True
        else:
            self.evolve = False

        #set_attack_time(self, elname)
        parse_config(self, conf)

        if self.is_training:
            logging.info("Learning Phase")
        else:
            logging.info("Detection Phase")

        self.run()

    def quit(self):
        self.packet_capturer.quit()
        self.window_manager.quit()
        self.feature_extractor.quit()
        self.model_manager.quit()
        self.causal_analyzer.quit()

    # The following is a routine for the experiment
    def run(self):
        logging.info("Training a model by running TCPReplay with {}".format(self.training_set_name))
        self.is_training = True

        if self.local:
            cmd = ["tcpreplay", "-i", "lo", self.training_set_name]
            self.tcpreplay_start_for_training = True
            subprocess.call(cmd)
        else:
            for i in range(2):
                msg = "training:{}:{}:{}".format(i, self.sidx, int(time.time()) + 10).encode()
                self.sock.sendto(msg, (self.ipaddr[i], self.ports[i]))
                msg, srvr = self.sock.recvfrom(256)
                msg = msg.decode()
                logging.info("msg: {} from {}".format(msg, srvr))
                op, avail = msg.split(":")

                if op != "training":
                    logging.error("Error in running the packet generator")
                    sys.exit(1)

                if avail == "unavailable":
                    logging.error("Dataset {} is unavailable in {}".format(self.sidx, srvr))
                    sys.exit(1)

            self.tcpreplay_start_for_training = True

            msg, srvr = self.sock.recvfrom(256)
            op, done = msg.decode().split(":")

            if op != "training":
                logging.error("Error in finishing the packet generator")
                sys.exit(1)

            if done != "done":
                logging.error("Error: the packet generator are incorrectly quitted")
                sys.exit(1)

            msg, srvr = self.sock.recvfrom(256)
            op, done = msg.decode().split(":")

            if op != "training":
                logging.error("Error in finishing the packet generator")
                sys.exit(1)

            if done != "done":
                logging.error("Error: the packet generator are incorrectly quitted")
                sys.exit(1)

        logging.info("Training packets have been sent")

#        while self.window_manager.get_cnt() < self.training_set_info["Total Packets"]:
#            time.sleep(1)
#            pass

        logging.info("Training packets captured: {}".format(self.packet_capturer.get_cnt()))

        while not self.is_training_set_processed:
            time.sleep(1)
            curr = time.time()
            if self.check_queue_lengths() and curr > self.training_start_time + self.training_set_info["Total Time"] + self.window_manager.get_period() + OFFSET:
                self.is_training_set_processed = True

        self.tcpreplay_end_for_training = True
        logging.info("Training packets processed: {}".format(self.packet_capturer.get_cnt()))

        logging.info("self.model_manager.get_is_model_generated()".format(self.model_manager.get_is_model_generated()))
        while not self.model_manager.get_is_model_generated():
            time.sleep(1)
            pass 
        logging.info("Total Number of Samples used to generate Models: {}".format(self.model_manager.get_cnt()))
        logging.info("Total Number of Anomalous Samples used to generate Models: {}".format(self.model_manager.get_acnt()))
        self.is_training = False

        time.sleep(3)
        logging.info("Testing the model with {}".format(self.test_set_name))

        self.is_testing = True
        if self.local:
            cmd = ["tcpreplay", "-i", "lo", self.test_set_name]
            self.tcpreplay_start_for_testing = True
            subprocess.call(cmd)
        else:
            for i in range(2):
                msg = "test:{}:{}:{}".format(i, self.sidx, int(time.time()) + 10).encode()
                self.sock.sendto(msg, (self.ipaddr[i], self.ports[i]))
                msg, srvr = self.sock.recvfrom(256)
                msg = msg.decode()
                logging.info("msg: {} from {}".format(msg, srvr))
                op, avail = msg.split(":")

                if op != "test":
                    logging.error("Error in running the packet generator")
                    sys.exit(1)

                if avail == "unavailable":
                    logging.error("Dataset {} is unavailable in {}".format(self.sidx, srvr))
                    sys.exit(1)

            self.tcpreplay_start_for_testing = True

            msg, srvr = self.sock.recvfrom(256)
            op, done = msg.decode().split(":")

            if op != "test":
                logging.error("Error in finishing the packet generator")
                sys.exit(1)

            if done != "done":
                logging.error("Error: the packet generator are incorrectly quitted")
                sys.exit(1)

            msg, srvr = self.sock.recvfrom(256)
            op, done = msg.decode().split(":")

            if op != "test":
                logging.error("Error in finishing the packet generator")
                sys.exit(1)

            if done != "done":
                logging.error("Error: the packet generator are incorrectly quitted")
                sys.exit(1)

        logging.info("Test packets have been sent")

        while self.packet_capturer.get_cnt() < self.test_set_info["Total Packets"] * 0.7:
            time.sleep(1)
            pass

        logging.info("Test packets captured: {}".format(self.packet_capturer.get_cnt()))
        self.tcpreplay_end_for_testing = True
        
        while not self.is_test_set_processed:
            time.sleep(1)
            curr = time.time()
            if self.check_queue_lengths() and curr > self.test_start_time + self.test_set_info["Total Time"] + self.window_manager.get_period() + OFFSET:
                self.is_test_set_processed = True

        logging.info("Test packets processed: {}".format(self.packet_capturer.get_cnt()))
        while not self.model_manager.get_is_test_finished():
            time.sleep(1)
            pass
        self.is_testing = False

        if self.evolve:
            while not self.model_manager.get_is_evolve_finished():
                time.sleep(1)
                pass

            self.is_retesting = True
            if self.local:
                cmd = ["tcpreplay", "-i", "lo", self.retest_set_name]
                self.tcpreplay_start_for_retesting = True
                subprocess.call(cmd)
            else:
                for i in range(2):
                    msg = "retest:{}:{}:{}".format(i, self.eidx, int(time.time()) + 10).encode()
                    self.sock.sendto(msg, (self.ipaddr[i], self.ports[i]))
                    msg, srvr = self.sock.recvfrom(256)
                    msg = msg.decode()
                    logging.info("msg: {} from {}".format(msg, srvr))
                    op, avail = msg.split(":")

                    if op != "retest":
                        logging.error("Error in running the packet generator")
                        sys.exit(1)

                    if avail == "unavailable":
                        logging.error("Dataset {} is unavailable in {}".format(self.sidx, srvr))
                        sys.exit(1)

                self.tcpreplay_start_for_retesting = True

                msg, srvr = self.sock.recvfrom(256)
                op, done = msg.decode().split(":")
    
                if op != "retest":
                    logging.error("Error in finishing the packet generator")
                    sys.exit(1)

                if done != "done":
                    logging.error("Error: the packet generator are incorrectly quitted")
                    sys.exit(1)

                msg, srvr = self.sock.recvfrom(256)
                op, done = msg.decode().split(":")

                if op != "retest":
                    logging.error("Error in finishing the packet generator")
                    sys.exit(1)

                if done != "done":
                    logging.error("Error: the packet generator are incorrectly quitted")
                    sys.exit(1)

            logging.info("Retest packets have been sent")

            while self.packet_capturer.get_cnt() < self.retest_set_info["Total Packets"] * 0.7:
                time.sleep(1)
                pass

            logging.info("Retest packets captured: {}".format(self.packet_capturer.get_cnt()))
            self.tcpreplay_end_for_retesting = True
        
            while not self.is_retest_set_processed:
                time.sleep(1)
                curr = time.time()
                if self.check_queue_lengths() and curr > self.test_start_time + self.test_set_info["Total Time"] + self.window_manager.get_period() + OFFSET:
                    self.is_retest_set_processed = True

            logging.info("Retest packets processed: {}".format(self.packet_capturer.get_cnt()))
            while not self.model_manager.get_is_retest_finished():
                time.sleep(1)
                pass
            self.is_retesting = False

        else:
            while not self.sequence_manager.get_is_sent():
                time.sleep(1)
                pass
        self.model_manager.print_result()
        self.write_result(self.output)


        logging.info("Quitting the experiment")
        #self.quit()

    def is_self_evolving(self):
        return self.evolve

    def write_result(self, ofname):
        training_set = self.model_manager.get_training_set()
        num_of_training_samples = len(training_set.get_dataset())

        with open(ofname, "w") as of:
            of.write("type, algorithm, accuracy, precision, recall, f1, true positive, true negative, false positive, false negative, learning time, first detection time, # of training samples, # of anomalous training samples, # of test samples, # of benign test samples, # of anomalous test samples\n")

            for aname in self.model_manager.get_anames():
                accuracy = self.model_manager.get_accuracy("attack", aname)
                precision = self.model_manager.get_precision("attack", aname)
                recall = self.model_manager.get_recall("attack", aname)
                f1 = self.model_manager.get_f1("attack", aname)
                tp = self.model_manager.get_tp("attack", aname)
                tn = self.model_manager.get_tn("attack", aname)
                fp = self.model_manager.get_fp("attack", aname)
                fn = self.model_manager.get_fn("attack", aname)
                lt = round(self.model_manager.get_learning_time("attack", aname), 2)
                fdt = self.model_manager.get_first_detection_time("attack", aname)
                if fdt != None:
                    fstr = str(round(fdt, 2))
                else:
                    fstr = "N/A"
                num_of_attack_training_samples = training_set.get_num_of_types("attack")
                num_of_test_samples = len(self.model_manager.test_labels["attack"])
                num_of_benign_test_samples = self.model_manager.get_num_of_benign_windows()
                num_of_attack_test_samples = self.model_manager.get_num_of_attack_windows()
            
                s = "attack, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}\n".format(aname, accuracy, precision, recall, f1, tp, tn, fp, fn, lt, fstr, num_of_training_samples, num_of_attack_training_samples, num_of_test_samples, num_of_benign_test_samples, num_of_attack_test_samples)
                logging.debug("{}: {}".format(ofname, s))
                of.write(s)

            for iname in self.model_manager.get_inames():
                accuracy = self.model_manager.get_accuracy("infection", iname)
                precision = self.model_manager.get_precision("infection", iname)
                recall = self.model_manager.get_recall("infection", iname)
                f1 = self.model_manager.get_f1("infection", iname)
                tp = self.model_manager.get_tp("infection", iname)
                tn = self.model_manager.get_tn("infection", iname)
                fp = self.model_manager.get_fp("infection", iname)
                fn = self.model_manager.get_fn("infection", iname)
                lt = round(self.model_manager.get_learning_time("infection", iname), 2)
                fdt = self.model_manager.get_first_detection_time("infection", iname)
                if fdt != None:
                    fstr = str(round(fdt, 2))
                else:
                    fstr = "N/A"
                num_of_infection_training_samples = training_set.get_num_of_types("infection")
                num_of_test_samples = len(self.model_manager.test_labels["infection"])
                num_of_benign_test_samples = self.model_manager.get_num_of_benign_windows()
                num_of_infection_test_samples = self.model_manager.get_num_of_infection_windows()

                s = "infection, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}\n".format(iname, accuracy, precision, recall, f1, tp, tn, fp, fn, lt, fstr, num_of_training_samples, num_of_infection_training_samples, num_of_test_samples, num_of_benign_test_samples, num_of_infection_test_samples)
                logging.debug("{}: {}".format(ofname, s))
                of.write(s)

            for rname in self.model_manager.get_rnames():
                accuracy = self.model_manager.get_accuracy("reconnaissance", rname)
                precision = self.model_manager.get_precision("reconnaissance", rname)
                recall = self.model_manager.get_recall("reconnaissance", rname)
                f1 = self.model_manager.get_f1("reconnaissance", rname)
                tp = self.model_manager.get_tp("reconnaissance", rname)
                tn = self.model_manager.get_tn("reconnaissance", rname)
                fp = self.model_manager.get_fp("reconnaissance", rname)
                fn = self.model_manager.get_fn("reconnaissance", rname)
                lt = round(self.model_manager.get_learning_time("reconnaissance", rname), 2)
                fdt = self.model_manager.get_first_detection_time("reconnaissance", rname)
                if fdt != None:
                    fstr = str(round(fdt, 2))
                else:
                    fstr = "N/A"
                num_of_reconnaissance_training_samples = training_set.get_num_of_types("reconnaissance")
                num_of_test_samples = len(self.model_manager.test_labels["reconnaissance"])
                num_of_benign_test_samples = self.model_manager.get_num_of_benign_windows()
                num_of_reconnaissance_test_samples = self.model_manager.get_num_of_reconnaissance_windows()
           
                s = "reconnaissance, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}\n".format(rname, accuracy, precision, recall, f1, tp, tn, fp, fn, lt, fstr, num_of_training_samples, num_of_reconnaissance_training_samples, num_of_test_samples, num_of_benign_test_samples, num_of_reconnaissance_test_samples)
                logging.debug("{}: {}".format(ofname, s))
                of.write(s)

            if self.evolve:
                for iname in self.model_manager.get_inames():
                    accuracy = self.model_manager.get_accuracy("evolution", iname)
                    precision = self.model_manager.get_precision("evolution", iname)
                    recall = self.model_manager.get_recall("evolution", iname)
                    f1 = self.model_manager.get_f1("evolution", iname)
                    tp = self.model_manager.get_tp("evolution", iname)
                    tn = self.model_manager.get_tn("evolution", iname)
                    fp = self.model_manager.get_fp("evolution", iname)
                    fn = self.model_manager.get_fn("evolution", iname)
                    lt = round(self.model_manager.get_learning_time("evolution", iname), 2)
                    fdt = self.model_manager.get_first_detection_time("evolution", iname)
                    if fdt != None:
                        fstr = str(round(fdt, 2))
                    else:
                        fstr = "N/A"
                    num_of_infection_training_samples = training_set.get_num_of_types("infection")
                    num_of_test_samples = len(self.model_manager.test_labels["evolution"])
                    num_of_benign_test_samples = self.model_manager.get_num_of_ebenign_windows()
                    num_of_infection_test_samples = self.model_manager.get_num_of_einfection_windows()

                    s = "evolution, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}\n".format(iname, accuracy, precision, recall, f1, tp, tn, fp, fn, lt, fstr, num_of_training_samples, num_of_infection_training_samples, num_of_test_samples, num_of_benign_test_samples, num_of_infection_test_samples)
                    logging.debug("{}: {}".format(ofname, s))
                    of.write(s)

    def get_tcpreplay_start_for_training(self):
        return self.tcpreplay_start_for_training

    def get_tcpreplay_end_for_training(self):
        return self.tcpreplay_end_for_training

    def get_tcpreplay_start_for_testing(self):
        return self.tcpreplay_start_for_testing

    def get_tcpreplay_end_for_testing(self):
        return self.tcpreplay_end_for_testing

    def get_tcpreplay_start_for_retesting(self):
        return self.tcpreplay_start_for_retesting

    def get_tcpreplay_end_for_retesting(self):
        return self.tcpreplay_end_for_retesting

    def get_is_training(self):
        return self.is_training

    def get_is_training_set_processed(self):
        return self.is_training_set_processed

    def get_is_testing(self):
        return self.is_testing

    def get_is_test_set_processed(self):
        return self.is_test_set_processed

    def get_is_retesting(self):
        return self.is_retesting

    def get_is_retest_set_processed(self):
        return self.is_retest_set_processed

    def set_training_start_time(self, timestamp):
        self.training_start_time = timestamp

    def get_training_start_time(self):
        return self.training_start_time

    def set_test_start_time(self, timestamp):
        self.test_start_time = timestamp

    def get_test_start_time(self):
        return self.test_start_time

    def set_retest_start_time(self, timestamp):
        self.retest_start_time = timestamp

    def get_retest_start_time(self):
        return self.retest_start_time

    def check_queue_lengths(self):
        logging.debug("packet_capturer: {}".format(self.packet_capturer.get_queue_length()))
        logging.debug("window_manager: {}".format(self.window_manager.get_queue_length()))
        logging.debug("feature_extractor: {}".format(self.feature_extractor.get_queue_length()))
        logging.info("model_manager: {}".format(self.model_manager.get_queue_length()))
        return self.packet_capturer.get_queue_length() == 0 and self.window_manager.get_queue_length() == 0 and self.feature_extractor.get_queue_length() == 0 and self.model_manager.get_queue_length() == 0

    def set_model_is_generated(self, val):
        self.model_is_generated = val
    
    def get_model_is_generated(self):
        return self.model_is_generated

    def get_training_set_label(self):
        return self.training_set_label

    def get_test_set_label(self):
        return self.test_set_label

    def set_attack_start_time(self, start_time):
        self.attack_start_time = start_time

    def get_attack_start_time(self):
        return self.attack_start_time

    def set_infection_start_time(self, start_time):
        self.infection_start_time = start_time

    def get_infection_start_time(self):
        return self.infection_start_time

    def set_reconnaissance_start_time(self, start_time):
        self.reconnaissance_start_time = start_time

    def get_reconnaissance_start_time(self):
        return self.reconnaissance_start_time

    def set_attack_end_time(self, end_time):
        self.attack_end_time = end_time

    def get_attack_end_time(self):
        return self.attack_end_time

    def send_packet_to_window_manager(self, pkt):
        self.window_manager.add_packet(pkt)

    def send_window_to_feature_extractor(self, window):
        self.feature_extractor.add_window(window)

    def send_window_to_encoding_manager(self, window):
        self.encoding_manager.add_window(window)

    def send_window_to_model_manager(self, window):
        self.model_manager.add_window(window)

    def send_identified_infections_to_model_manager(self, serials):
        self.model_manager.update_model(serials)

    def send_window_to_episode_manager(self, aname, window):
        self.episode_manager.add_window(aname, window)

    def send_training_set_to_sequence_manager(self, training_set):
        self.sequence_manager.process_training_set(training_set)

    def send_window_to_sequence_manager(self, window):
        self.sequence_manager.add_window(window)

def parse_config(ids, conf):
    wsize = -1
    swnd = True
    max_len = -1
    min_fr = -1
    min_conf = -1
    fixed = False
    granularity = 1
    width = 100
    efname = None
    features = {}
    states = {}
    home = "."
    rv = 2
    ipaddr = "127.0.0.1"
    port = 20000
    ofprefix = "sequence"
    anames = None
    inames = None
    rnames = None
    local = False
    ipaddr0 = None
    ipaddr1 = None
    port0 = 20001
    port1 = 20001
    strategy = 1

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
                elif key == "Sliding Window":
                    if val.lower() == "true":
                        swnd = True
                    elif val.lower() == "false":
                        swnd = False
                    else:
                        swnd = None
                elif key == "Episode Maximum Length":
                    max_len = int(val)
                elif key == "Episode Minimum Frequency":
                    min_fr = float(val)
                elif key == "Episode Minimum Confidence":
                    min_conf = float(val)
                elif key == "Fixed Length Episode":
                    if "True" in val:
                        fixed = True
                elif key == "Batch Granularity":
                    granularity = float(val)
                elif key == "Batch Width":
                   width = int(val)
                elif key == "Classes":
                    lst = val.split(", ")
                    for i in range(len(lst)):
                        states[i] = lst[i]
                elif key == "Home Directory":
                    home = val
                    home = os.path.abspath(home)
                    if not os.path.exists(home):
                        os.mkdir(home)
                    ids.output = "{}/{}".format(home, ids.output)
                elif key == "Round Value":
                    rv = int(val)
                elif key == "IP Address":
                    ipaddr = val
                elif key == "Port":
                    port = int(val)
                elif key == "Output Prefix":
                    ofprefix = val
                elif key == "Analysis Result Prefix":
                    rfprefix = val
                elif key == "Number Of Candidates":
                    ncandidates = val
                elif key == "Number Of Results":
                    nresults = val
                elif key == "Number Of Final Results":
                    nfinal = val
                elif key == "Local":
                    if "True" in val:
                        local = True
                elif key == "IP Address 0":
                    ipaddr0 = val
                elif key == "Port 0":
                    port0 = int(val)
                elif key == "IP Address 1":
                    ipaddr1 = val
                elif key == "Port 1":
                    port1 = int(val)
                elif key == "Episode Output":
                    efname = val
                elif key == "Update Strategy":
                    strategy = val
                elif key == "Encoder":
                    ename = val
                elif key == "Attack Detection":
                    anames = val.split(",")
                    for i in range(len(anames)):
                        anames[i] = anames[i].strip()
                elif key == "Infection Detection":
                    inames = val.split(",")
                    for i in range(len(inames)):
                        inames[i] = inames[i].strip()
                elif key == "Reconnaissance Detection":
                    rnames = val.split(",")
                    for i in range(len(rnames)):
                        rnames[i] = rnames[i].strip()
                elif key == "Analyzer":
                    cnames = val.split(",")
                    for i in range(len(cnames)):
                        cnames[i] = cnames[i].strip()
                else:
                    if val.lower() == "true":
                        tf = True
                    elif val.lower() == "false":
                        tf = False
                    else:
                        continue
                    features[key] = tf
            except:
                logging.error("Error in parsing the line: {}".format(line))
                continue

    if not local and (not ipaddr0 or not ipaddr1):
        logging.error("\"IP Address 0\" and \"IP Address 1\"  should be specified")
        sys.exit(1)
    else:
        ids.local = local
        ids.ipaddr[0] = ipaddr0
        ids.ipaddr[1] = ipaddr1
        ids.ports[0] = port0
        ids.ports[1] = port1

    #ids.packet_capturer = PacketCapturer(ids, ids.get_training_set_label(), ids.get_test_set_label())
    ids.packet_capturer = PacketCapturer(ids)
    logging.debug("PacketCapturer is initialized")

    if wsize < 0:
        logging.error("Window Size is not set: {}".format(wsize))
        sys.exit(1)

    if swnd == None:
        logging.error("Sliding Window is not set")
        sys.exit(1)

    ids.window_manager = WindowManager(ids, wsize, swnd)
    logging.debug("WindowManager is initialized with the window size: {}".format(wsize))

    if len(features) <= 0:
        logging.error("Features are not correctly set")
        sys.exit(1)
    ids.feature_extractor = FeatureExtractor(ids, features)
    logging.debug("FeatureExtractor is initialized with the features: {}".format(features))

    if ename == None:
        logging.error("Encoder is not set")
        sys.exit(1)
    ids.encoding_manager = EncodingManager(ids, ename)
    logging.debug("EncodingManager is initialized with the encoder: {}".format(ename))

    if not anames:
        logging.error("Attack Detection Algorithm is not set")
        anames = []
    if not inames:
        logging.error("Infection Detection Algorithm is not set")
        inames = []
    if not rnames:
        logging.error("Reconnaissance Detection Algorithm is not set")
        rnames = []

    ids.model_manager = ModelManager(ids, anames, inames, rnames, strategy)
    logging.debug("ModelManager is initialized with the attack detection algorithm: {}".format(anames))
    logging.debug("ModelManager is initialized with the infection detection algorithm: {}".format(inames))
    logging.debug("ModelManager is initialized with the reconnaissance detection algorithm: {}".format(rnames))

    if len(cnames) <= 0:
        logging.error("No causal analyzer is set")
        sys.exit(1)

    ids.sequence_manager = SequenceManager(ids, home, ofprefix, rv, ipaddr, port, max_len, width, granularity, cnames)
    logging.debug("SequenceManager is initialized")

def parse_label(fname):
    ret = {}
    ret["none"] = {}
    with open(fname, "r") as f:
        cnt = 1
        for line in f:
            tmp = line.strip().split(", ")
            num = int(tmp[0])
            while cnt < num:
                ret["none"][cnt] = 1
                cnt += 1
            ret["none"][cnt] = 0
            key = "{}:{}-{}:{}".format(tmp[3], int(tmp[4]), tmp[5], int(tmp[6]))
            if key not in ret:
                ret[key] = {}
            ret[key][cnt] = int(tmp[-1])
            cnt += 1
    ret["none"][cnt] = 0
    return ret

def parse_info(fname):
    ret = {}
    with open(fname, "r") as f:
        for line in f:
            tmp = line.strip().split(": ")
            key = tmp[0].strip()
            val = float(tmp[1].strip())
            ret[key] = val
    return ret

def set_attack_time(ids, fname):
    with open(fname, "r") as f:
        line = f.readline()
        tmp = line.strip().split(", ")
        ids.set_attack_start_time(float(tmp[1]))
        for line in f:
            pass
        tmp = line.strip().split(", ")
        ids.set_attack_end_time(float(tmp[1]))

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--conf", required=True, metavar="<configuration file>", help="Configuration File", type=str)
    parser.add_argument("-d", "--dataset", required=True, metavar="<dataset (1/2/3/4/5)>", help="Dataset (1/2/3/4/5)", type=int)
    parser.add_argument("-e", "--evolve", metavar="<retest dataset>", help="Dataset used for the test after evolvement", type=int, default=-1)
    parser.add_argument("-o", "--output", metavar="<output file name prefix>", help="Output File Name Prefix", type=str, default="output")
    parser.add_argument("-s", "--serial", metavar="<serial number>", help="Serial Number", type=int, default=None)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)
    ids = IDSCore(args.conf, args.dataset, args.output, args.serial, args.evolve)

if __name__ == "__main__":
    main()
