import sys
import logging
from features.feature import Feature

class TotalBackwardPackets(Feature):
    def __init__(self, name):
        super().__init__(name, "flow")

    # Please implement the following function
    def extract_feature(self, window):
        logging.debug("Feature: {}".format(self.get_name()))
        key = self.get_name()
        value = len(window.get_packets("backward"))
        window.add_feature_value(key, value)
        logging.debug("{}: {}".format(key, value))
