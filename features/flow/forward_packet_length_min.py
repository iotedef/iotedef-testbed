import sys
import logging
from features.feature import Feature

class ForwardPacketLengthMin(Feature):
    def __init__(self, name):
        super().__init__(name, "flow")

    # Please implement the following function
    def extract_feature(self, window):
        pkts = window.get_packets("forward")

        if len(pkts) > 0:
            min_len = 65536 # the maximum size of the IP datagram

            for pkt in pkts:
                plen = pkt.get_packet_length()
                if plen < min_len:
                    min_len = plen
        else:
            min_len = -1

        window.add_feature_value(self.get_name(), min_len)
        logging.debug("{}: {}".format(self.get_name(), min_len))
