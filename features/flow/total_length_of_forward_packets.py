import sys
import logging
from features.feature import Feature

class TotalLengthOfForwardPackets(Feature):
    def __init__(self, name):
        super().__init__(name, "flow")

    # Please implement the following function
    def extract_feature(self, window):
        pkts = window.get_packets("forward")

        lst = []
        for pkt in pkts:
            lst.append(pkt.get_packet_length())

        totlen = sum(lst)
        window.add_feature_value(self.get_name(), totlen)
        logging.debug("{}: {}".format(self.get_name(), totlen))
