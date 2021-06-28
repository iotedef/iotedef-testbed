import sys
import copy
import logging
import numpy as np
from algorithms.algorithm import Algorithm
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.metrics import Recall, Precision
from sklearn.preprocessing import MinMaxScaler, StandardScaler

THRESHOLD=0.5

class Feedforward(Algorithm):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    # Concerning dataset, refer to the class TrainingSet
    def learning(self, windows, kind):
        dataset = copy.deepcopy(windows.get_dataset(kind))
        dataset = np.array(dataset)
        self.scale = StandardScaler().fit(dataset)
        dataset = self.scale.transform(dataset)
        dataset = dataset.reshape((dataset.shape[0], 1, dataset.shape[1]))
        features = len(windows.get_feature_names())
        tmp = windows.get_labels(kind)
        labels = []
        for l in tmp:
            labels.append([l])
        labels = np.array(labels)

        self.classifier[kind] = Sequential()
        self.classifier[kind].add(Dense(128, activation='relu', input_shape=(1,features), input_dim=features))
        self.classifier[kind].add(Dense(128, activation='relu'))
        self.classifier[kind].add(Dense(1, activation='sigmoid'))
        self.classifier[kind].compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        try:
            self.classifier[kind].fit(dataset, labels, epochs=20, batch_size=1, verbose=1)
            logging.info("{} {} classifier is generated".format(self.get_name(), kind))
        except:
            self.classifier[kind] = None
            logging.info("{} {} classifier is not generated".format(self.get_name(), kind))

    def detection(self, window, kind):
        label = window.get_label(kind)
        test = window.get_code().copy()
        test = np.array(test)
        test = self.scale.transform(test)
        test = test.reshape((test.shape[0], 1, test.shape[1]))
        pred = list(self.classifier[kind].predict(test)[0][0])
        val = pred[0]
        pred.insert(0, 1-val)
        ret = (val >= THRESHOLD).astype("int32")
        logging.debug("label: {}, pred: {}, ret: {}".format(label, pred, ret))
        return [ret], list(pred)
