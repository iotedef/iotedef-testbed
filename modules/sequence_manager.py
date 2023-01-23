import argparse
import time
import logging
import socket
import sys
import threading
sys.path.append("..")
from definitions.states import State
from definitions.sequence import Sequence

BUF_SIZE = 256

class SequenceManager:
    def __init__(self, core, home, ofprefix, rv, ipaddr, port, max_len, width, granularity, anames):
        self.core = core
        self.sequence = []
        self.home_directory = home
        self.ofprefix = ofprefix
        self.rv = rv
        self.max_len = max_len
        self.width = width
        self.granularity = granularity
        self.anames = anames
        self.ipaddr = ipaddr
        self.port = port
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sent = False

        mr = threading.Thread(target=self.monitor_and_run, daemon=True)
        mr.start()

    def process_training_set(self, training_set):
        windows = training_set.get_windows()
        states = []
        fnames = windows[0].get_feature_names()

        for window in windows:
            values = []
            for f in fnames:
                values.append(window.get_feature_value(f))
            # The sequence below is to generate the model; thus, the answer labels should be inputted (i.e., window.get_label())
            states.append(State(window.get_serial_number(), window.get_flow_info("forward"), fnames, values, window.get_label(), window.get_labeled(), window.get_probability(), round(window.get_window_start_time(), self.rv), round(window.get_window_end_time(), self.rv), True))

        start_time = round(states[0].get_start_time(), self.rv)
        end_time = round(states[-1].get_end_time(), self.rv)
        ofname = "{}/{}_{}.csv".format(self.home_directory, self.ofprefix, int(time.time()))
        sequence = Sequence(states, start_time, end_time, self.granularity, self.width)
        logging.info(">>> Store the sequence for training as {}".format(ofname))
        sequence.store(ofname, training=True)
        algs = ""
        for a in self.anames[:-1]:
            algs += "{},".format(a)
        algs += "{}".format(self.anames[-1])

        msg = "training:{}:{}".format(algs, ofname)
        self.sock.sendto(str.encode(msg), (self.ipaddr, self.port))

    def get_is_sent(self):
        return self.sent

    def add_window(self, window):
        fnames = window.get_feature_names()

        values = []
        for f in fnames:
            values.append(window.get_feature_value(f))

        # The sequence below is to be analyzed; thus, the output of the classification should be inputted (i.e., window.get_labeled())
        state = State(window.get_serial_number(), window.get_flow_info("forward"), fnames, values, window.get_label(), window.get_labeled(), window.get_probability(), round(window.get_window_start_time(), self.rv), round(window.get_window_end_time(), self.rv), False)
        self.sequence.append(state)

        # TODO: Change the following
        #if window.get_labeled("attack") == 1:
        #print ("self.tested: {}, window.get_label('attack'): {}, window.get_labeled('attack'): {}".format(self.tested, window.get_label("attack"), window.get_labeled("attack")))
        #if not self.tested and window.get_label("attack") == 1 and window.get_labeled("attack") == 1:
    
    def monitor_and_run(self):
        sent = False
        while not sent:
            if len(self.sequence) > 0 and not self.core.get_is_testing() and not self.core.get_is_retesting():
                start_time = round(self.sequence[0].get_start_time(), self.rv)
                end_time = round(self.sequence[-1].get_end_time(), self.rv)
                ofname = "{}/{}_{}.csv".format(self.home_directory, self.ofprefix, int(time.time()))
                sequence = Sequence(self.sequence, start_time, end_time, self.granularity, self.width)
                logging.info(">>> Store the sequence for testing as {}".format(ofname))
                sequence.store(ofname, training=False)

                algs = ""
                for a in self.anames[:-1]:
                    algs += "{},".format(a)
                algs += "{}".format(self.anames[-1])

                if self.core.is_self_evolving():
                    msg = "evolve:{}:{}".format(algs, ofname)
                else:
                    msg = "test:{}:{}".format(algs, ofname)
                self.sock.sendto(str.encode(msg), (self.ipaddr, self.port))
                logging.info("send to the causal analyzer")

                if self.core.is_self_evolving():
                    wait = threading.Thread(target=self.wait, daemon=True)
                    wait.start()

                sent = True
            time.sleep(1)
        self.sent = True

    def wait(self):
        logging.info("Wait for self-evolvement")
        msg, _ = self.sock.recvfrom(BUF_SIZE)
        msg = msg.decode()
        op, s = msg.split(":")
        serials = []
        tmp = s.split(",")
        for serial in tmp:
            try:
                serials.append(int(serial))
            except:
                continue
        logging.debug("Received message: {}".format(msg))
        logging.info("Received serial ({}): {}".format(len(serials), serials))

        if op == "update":
            logging.debug("update message")

            self.core.send_identified_infections_to_model_manager(serials)
        else:
            logging.debug("error command")
