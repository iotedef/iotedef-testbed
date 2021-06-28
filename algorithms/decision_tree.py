import sys
import copy
import logging
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_graphviz
from sklearn.preprocessing import StandardScaler
from six import StringIO
from IPython.display import Image
from algorithms.algorithm import Algorithm

class DecisionTree(Algorithm):
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

        self.classifier[kind] = DecisionTreeClassifier()

        try:
            self.classifier[kind] = self.classifier[kind].fit(dataset, labels)
            logging.info("{} {} classifier is generated".format(self.get_name(), kind))
        except:
            self.classifier[kind] = None
            logging.info("{} {} classifier is not generated".format(self.get_name(), kind))

    def detection(self, window, kind):
        test = window.get_code().copy()
        test = np.array(test)
        test = self.scale.transform(test)
        if self.classifier[kind]:
            pred = self.classifier[kind].predict_proba(test)
            ret = self.classifier[kind].predict(test)
            logging.debug("{}> pred: {}, ret: {}".format(self.get_name(), pred, ret))
            return ret, list(pred[0])
        else:
            logging.debug("{}> pred: {}, ret: {}".format(self.get_name(), pred, ret))
            return [0], [0, 1]
