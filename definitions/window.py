from definitions.flow import Flow
from utils.network import extract_flow_info
import logging
import numpy as np

class Window:
    def __init__(self, protocol, saddr, sport, daddr, dport, period, dummy=False):
        self.flow = {}
        self.flow["forward"] = Flow(protocol, saddr, sport, daddr, dport)
        self.flow["backward"] = Flow(protocol, daddr, dport, saddr, sport)
        self.packets = {}
        self.packets["forward"] = []
        self.packets["backward"] = []
        self.stat = {} # map: feature -> value
        self.period = period
        self.code = None
        if dummy:
            self.dummy = True
        else:
            self.dummy = False

        self.label = {}
        self.label["attack"] = 0
        self.label["infection"] = 0
        self.label["reconnaissance"] = 0

        self.labeled = {}
        self.labeled["attack"] = 0
        self.labeled["infection"] = 0
        self.labeled["reconnaissance"] = 0

        self.probability = {}
        self.probability["attack"] = 0
        self.probability["infection"] = 0
        self.probability["reconnaissance"] = 0
        self.probability["benign"] = 0

        self.window_start_time = None
        self.window_end_time = None
        self.serial = 0
        self.flow_info = {}
        self.flow_info["forward"] = "{}:{}-{}:{}".format(saddr, sport, daddr, dport)
        self.flow_info["backward"] = "{}:{}-{}:{}".format(daddr, dport, saddr, sport)

    def is_dummy(self):
        return self.dummy

    def is_corresponding_flow(self, window):
        ret1 = self.flow["forward"].is_corresponding_flow(window.get_flow("forward"))
        ret2 = self.flow["forward"].is_corresponding_flow(window.get_flow("backward"))
        ret3 = self.flow["backward"].is_corresponding_flow(window.get_flow("forward"))
        ret4 = self.flow["backward"].is_corresponding_flow(window.get_flow("backward"))
        return ret1 or ret2 or ret3 or ret4

    def get_serial_number(self):
        return self.serial
    
    def set_serial_number(self, serial):
        self.serial = serial

    def get_flow_info(self, direction=None):
        if direction:
            return self.flow_info[direction]
        else:
            return self.flow_info

    def get_flow(self, direction):
        return self.flow[direction]

    def add_packet(self, pkt):
        protocol, saddr, sport, daddr, dport = pkt.get_each_flow_info()

        if self.flow["forward"].get_protocol() == protocol and self.flow["forward"].get_saddr() == saddr and self.flow["forward"].get_sport() == sport and self.flow["forward"].get_daddr() == daddr and self.flow["forward"].get_dport() == dport:
            self.packets["forward"].append(pkt)
        elif self.flow["backward"].get_protocol() == protocol and self.flow["backward"].get_saddr() == saddr and self.flow["backward"].get_sport() == sport and self.flow["backward"].get_daddr() == daddr and self.flow["backward"].get_dport() == dport:
            self.packets["backward"].append(pkt)

        if pkt.get_label() == 1:
            self.label["attack"] = 1
            logging.debug("Window is set to {} (attack)".format(self.label["attack"]))

        elif pkt.get_label() == 2:
            self.label["infection"] = 1
            logging.debug("Window is set to {} (infection)".format(self.label["infection"]))

        elif pkt.get_label() == 3:
            self.label["reconnaissance"] = 1
            logging.debug("Window is set to {} (reconnaissance)".format(self.label["reconnaissance"]))

    def get_packets(self, direction):
        return self.packets[direction]

    def set_packets(self, direction, pkts):
        self.packets[direction] = pkts
        for p in pkts:
            if p.get_label() == 1:
                self.label["attack"] = 1
            if p.get_label() == 2:
                self.label["infection"] = 1
            if p.get_label() == 3:
                self.label["reconnaissance"] = 1

    def add_feature_value(self, feature, val):
        if feature not in self.stat:
            self.stat[feature] = 0
        self.stat[feature] = self.stat[feature] + val

    def get_feature_value(self, feature):
        return self.stat[feature]

    def get_feature_names(self):
        return list(self.stat)

    def get_period(self):
        return self.period

    def set_code(self, code):
        self.code = code

    def get_code(self):
        return [self.code]

    def set_label(self, kind, label):
        self.label[kind] = label

    def get_label(self, kind=None):
        if kind:
            return self.label[kind]
        else:
            return self.label

    def get_best_label(self):
        ret = 0
        if self.label["attack"] == 1:
            ret = 1
        elif self.label["reconnaissance"] == 1:
            ret = 3
        elif self.label["infection"] == 1:
            ret = 2
        return ret

    def set_labeled(self, kind, label):
        self.labeled[kind] = label

    def get_labeled(self, kind=None):
        if kind:
            return self.labeled[kind]
        else:
            return self.labeled

    def set_probability(self, kind, prob):
        self.probability[kind] = prob

    def set_probability_complete(self):
        a = self.probability["attack"]
        i = self.probability["infection"]
        r = self.probability["reconnaissance"]
        b = self.probability["benign"] = (1-a) * (1-i) * (1-r)

        x = np.array([b, a, r, i])
        y = softmax(x)

        self.probability["benign"] = y[0]
        self.probability["attack"] = y[1]
        self.probability["reconnaissance"] = y[2]
        self.probability["infection"] = y[3]

    def get_probability(self, kind=None):
        if kind:
            return self.probability[kind]
        else:
            return self.probability

    def get_probability_vector(self):
        b = self.probability["benign"]
        a = self.probability["attack"]
        r = self.probability["reconnaissance"]
        i = self.probability["infection"]
        return np.array([b, a, r, i])

    def get_stat(self):
        return self.stat

    def set_times(self, start_time, end_time):
        self.window_start_time = start_time
        self.window_end_time = end_time

    def get_window_start_time(self):
        return self.window_start_time

    def get_window_end_time(self):
        return self.window_end_time

    def get_num_of_packets(self, kwd):
        ret = 0
        if kwd == "both":
            ret += len(self.packets["forward"] + self.packets["backward"])
        else:
            ret += len(self.packets[kwd])
        return ret

def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()
