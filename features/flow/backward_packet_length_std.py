import sys
import math
import logging
from features.feature import Feature

class BackwardPacketLengthStd(Feature):
    def __init__(self, name):
        super().__init__(name, "flow")

    # Please implement the following function
    def extract_feature(self, window):
        pkts = window.get_packets("backward")
        plst = []

        for pkt in pkts:
            plst.append(pkt.get_packet_length())

        if len(plst) > 0:
            avg = sum(plst) / len(plst)
        
            total = 0
            for p in plst:
                total = total + p * p

            var = total / len(plst) - avg * avg
            stdev = round(math.sqrt(var), 2)
        else:
            stdev = -1

        window.add_feature_value(self.get_name(), stdev)
        logging.debug("{}: {}".format(self.get_name(), stdev))
