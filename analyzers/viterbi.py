import sys
import logging
import numpy as np
import time
from hmmlearn.hmm import MultinomialHMM
from analyzers.analyzer import Analyzer

class Viterbi(Analyzer):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    def learning(self, sequence, config):
        logging.debug('Learning: {}'.format(self.get_name()))
        classes = ["B", "I", "A", "R"]
        states = sequence.get_sequence()
        input_sequence = []
        for state in states:
            input_sequence.append(state.get_best_label())
        input_sequence = np.array([input_sequence]).T
        startprob = np.array([0.25, 0.25, 0.25, 0.25])

        self.model = MultinomialHMM(n_components=4, transmat_prior=1.0)
        self.model.start_ = startprob
        try:
            self.model.fit(input_sequence)
            logging.info("HMM model is generated")
        except:
            self.model = None
            logging.info("HMM model is not generated")


    def analysis(self, sequence, config):
        logging.debug('Analysis: {}'.format(self.get_name()))

        states = sequence.get_sequence()
        input_sequence = []
        for state in states:
            input_sequence.append(state.get_best_label())
        input_sequence = np.array([input_sequence]).T

        _, output = self.model.decode(input_sequence, algorithm="viterbi")

        ret = []
        for i in range(len(output)):
            states[i].set_hidden_label_int(output[i])
            if output[i] == 2:
                prob = 0.0
                ret.append((prob, states[i]))

        self.print_infection_information(ret, config)
        logging.info("Analysis based on {} is finished".format(self.get_name()))

        return ret
