import sys
import logging
from features.feature import Feature

class FlowProtocol(Feature):
    def __init__(self, name):
        super().__init__(name, "flow")

    # Please implement the following function
    # The variable `val` should contain the result value
    def extract_feature(self, window):
        # TODO: Implement the procedure to extract the feature
        logging.debug("{}".format(self.get_name()))

        val = window.get_flow("forward").get_protocol()

        window.add_feature_value(self.get_name(), val)
        logging.debug('{}: {}'.format(self.get_name(), val))
