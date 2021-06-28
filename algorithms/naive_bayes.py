import sys
import copy
import logging
import numpy as np
from sklearn.naive_bayes import GaussianNB
from algorithms.algorithm import Algorithm
from sklearn.preprocessing import StandardScaler

class NaiveBayes(Algorithm):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    # Concerning dataset, refer to the class TrainingSet
    def learning(self, windows, kind):
        dataset = copy.deepcopy(windows.get_dataset(kind))
        dataset = np.array(dataset)
        self.scale = StandardScaler().fit(dataset)
        dataset = self.scale.transform(dataset)
        labels = windows.get_labels(kind)

        self.classifier[kind] = GaussianNB()
        try:
            self.classifier[kind] = self.classifier[kind].fit(dataset, labels)
            logging.info("{} {} classifier is generated".format(self.get_name(), kind))
        except:
            self.classifier[kind] = None
            logging.info("{} {} classifier is not generated".format(self.get_name(), kind))

    def detection(self, window, kind):
        test = window.get_code()
        test = np.array(test)
        test = self.scale.transform(test)
        label = window.get_label(kind)
        if self.classifier[kind]:
            pred = self.classifier[kind].predict_proba(test)
            ret = self.classifier[kind].predict(test)
            logging.debug("pred: {}, ret: {}".format(pred, ret))
            return ret, list(pred[0])
        else:
            return [0], [0, 1]
