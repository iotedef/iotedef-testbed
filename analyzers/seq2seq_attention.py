import sys
import logging
from analyzers.analyzer import Analyzer

class Seq2seqAttention(Analyzer):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    def learning(self, sequence, config):
        logging.debug('Learning: {}'.format(self.get_name()))
        states = sequence.get_sequence()
        features = len(states[0].get_code())
        rv = config["rv"]

        print ("len(states): {}".format(len(states)))

        self.model = None

    def analysis(self, sequence, config):
        logging.debug('Analysis: {}'.format(self.get_name()))

