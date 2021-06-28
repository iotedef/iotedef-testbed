import sys
import logging
from analyzers.analyzer import Analyzer

class Identity(Analyzer):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    def learning(self, sequence, config):
        logging.debug('Learning: {}'.format(self.get_name()))
        self.model = 1
        logging.info("Identify Analyzer is generated")

    def analysis(self, sequence, config):
        logging.debug('Analysis: {}'.format(self.get_name()))

        states = sequence.get_sequence()
        ret = []
        for i in range(len(states)):
            if states[i].get_labeled("infection") == 1:
                states[i].set_hidden_label_int(2)
                prob = 0.0
                ret.append((prob, states[i]))

        self.print_infection_information(ret, config)

        return ret
