import sys
import logging
from features.feature import Feature

class FlowPsh(Feature):
    def __init__(self, name):
        super().__init__(name, "flow")

    # Please implement the following function
    def extract_feature(self, window):
        logging.debug('{}'.format(self.get_name()))
        fpkts = window.get_packets("forward")
        bpkts = window.get_packets("backward")

        tot_num = 0

        pkts = fpkts + bpkts
        for pkt in pkts:
            if pkt.is_psh():
                tot_num += 1

        window.add_feature_value(self.get_name(), tot_num)
        logging.debug("{}: {}".format(self.get_name(), tot_num))
