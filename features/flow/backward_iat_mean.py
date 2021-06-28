import sys
import logging
from features.feature import Feature

class BackwardIatMean(Feature):
    def __init__(self, name):
        super().__init__(name, "flow")

    # Please implement the following function
    # The variable `val` should contain the result value
    def extract_feature(self, window):
        # TODO: Implement the procedure to extract the feature

        pkts = window.get_packets("backward")
        total = 0
        for i in range(len(pkts)):
            if i == 0:
                prep = pkts[i].get_timestamp()
            else:
                curr = pkts[i].get_timestamp()
                iat = curr - prep
                total += iat
        try:
            val = round(total / len(pkts), 2)
        except:
            val = -1

        window.add_feature_value(self.get_name(), val)
        logging.debug('{}: {}'.format(self.get_name(), val))
