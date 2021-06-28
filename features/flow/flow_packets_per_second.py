import sys
import logging
from features.feature import Feature

class FlowPacketsPerSecond(Feature):
    def __init__(self, name):
        super().__init__(name, "flow")

    # Please implement the following function
    def extract_feature(self, window):
        bpkts = window.get_packets("backward")
        fpkts = window.get_packets("forward")
        npackets = len(bpkts) + len(fpkts)
        fpps = round(npackets / window.get_period(), 2)

        window.add_feature_value(self.get_name(), fpps)
        logging.debug("{}: {}".format(self.get_name(), fpps))
