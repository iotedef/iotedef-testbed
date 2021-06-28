import sys
import copy
import logging
import numpy as np
from algorithms.algorithm import Algorithm
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Activation
from keras.layers import Dropout
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler

TIME_STEP = 2
THRESHOLD = 0.5

class Lstm(Algorithm):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    # Concerning dataset, refer to the class TrainingSet
    def learning(self, windows, kind):
        dataset = copy.deepcopy(windows.get_dataset(kind))
        dataset = np.array(dataset)
        self.scale = StandardScaler().fit(dataset)
        dataset = self.scale.transform(dataset)
        fallback = False
        try:
            dataset = dataset.reshape((dataset.shape[0], TIME_STEP, int(dataset.shape[1] / TIME_STEP)))
        except:
            fallback = True
            dataset = dataset.reshape((dataset.shape[0], 1, dataset.shape[1]))

        tmp = windows.get_labels(kind)
        labels = []
        for l in tmp:
            labels.append([l])
        labels = np.array(labels)
        features = len(windows.get_feature_names())

        self.classifier[kind] = Sequential()
        if fallback:
            self.classifier[kind].add(LSTM(128, return_sequences=True, activation='relu', input_shape=(1, features)))
        else:
            self.classifier[kind].add(LSTM(128, return_sequences=True, activation='relu', input_shape=(TIME_STEP, int(features / TIME_STEP))))
        self.classifier[kind].add(LSTM(128, return_sequences=True, activation='relu'))
        self.classifier[kind].add(Dense(1, activation='sigmoid'))
        self.classifier[kind].compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

        try:
            self.classifier[kind].fit(dataset, labels, epochs=10, validation_split=0.2, verbose=2)
            if fallback:
                logging.info("{} {} classifier is generated with the time step 1".format(self.get_name(), kind))
            else:
                logging.info("{} {} classifier is generated with the time step {}".format(self.get_name(), kind, TIME_STEP))
        except:
            self.classifier[kind] = None
            logging.info("{} {} classifier is not generated".format(self.get_name(), kind))

    def detection(self, window, kind):
        logging.debug("window.get_code(): {}".format(window.get_code()))
        label = window.get_label(kind)
        test = window.get_code().copy()
        test = np.array(test)
        test = self.scale.transform(test)
        fallback = False
        try:
            test = test.reshape((test.shape[0], TIME_STEP, int(test.shape[1] / TIME_STEP)))
        except:
            fallback = True
            test = test.reshape((test.shape[0], 1, test.shape[1]))

        pred = list(self.classifier[kind].predict(test)[0][0])
        val = pred[0]
        pred.insert(0, 1-val)
        ret = (val > THRESHOLD).astype("int32")

        if fallback:
            logging.debug("lstm> label: {}, pred: {}, ret: {}, time_step: 1".format(label, pred, ret))
        else:
            logging.debug("lstm> label: {}, pred: {}, ret: {}, time_step: {}".format(label, pred, ret, TIME_STEP))
        return [ret], list(pred)
