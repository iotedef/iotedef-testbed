import sys
import logging
from features.feature import Feature

class TotalForwardPackets(Feature):
    def __init__(self, name):
        super().__init__(name, "flow")

    def extract_feature(self, window):
        logging.debug("Feature: {}".format(self.get_name()))
        key = self.get_name()
        value = len(window.get_packets("forward"))
        logging.debug("{}: {}".format(key, value))
        window.add_feature_value(key, value)
