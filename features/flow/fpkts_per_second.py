import sys
import logging
from features.feature import Feature

class FpktsPerSecond(Feature):
    def __init__(self, name):
        super().__init__(name, "flow")

    # Please implement the following function
    # The variable `val` should contain the result value
    def extract_feature(self, window):
        # TODO: Implement the procedure to extract the feature
        pkts = window.get_packets("forward")
        val = round(len(pkts) / window.get_period(), 2)

        window.add_feature_value(self.get_name(), val)
        logging.debug('{}: {}'.format(self.get_name(), val))
