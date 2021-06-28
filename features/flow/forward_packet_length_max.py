import sys
import logging
from features.feature import Feature

class ForwardPacketLengthMax(Feature):
    def __init__(self, name):
        super().__init__(name, "flow")

    # Please implement the following function
    def extract_feature(self, window):
        pkts = window.get_packets("forward")
        max_len = -1

        for pkt in pkts:
            plen = pkt.get_packet_length()
            if plen > max_len:
                max_len = plen

        window.add_feature_value(self.get_name(), max_len)
        logging.debug("{}: {}".format(self.get_name(), window.get_feature_value(self.get_name())))
