import numpy as np
import sys
import logging
from encoders.encoder import Encoder

class Identity(Encoder):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following function
    def encoding(self, window):
        logging.debug('{}'.format(self.get_name()))
        names = window.get_feature_names()
        encoded = []
        
        for n in names:
            encoded.append(window.get_feature_value(n))

        logging.debug("Encoded Window: {}".format(encoded))
        window.set_code(encoded)
