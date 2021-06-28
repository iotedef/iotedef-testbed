import sys
import logging
import numpy as np
from analyzers.analyzer import Analyzer
from keras import Input, Model
from keras.layers import LSTM, Dense, Layer
from keras.regularizers import l2
import keras.backend as K
import tensorflow as tf

class Attention(Analyzer):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    def learning(self, sequence, config):
        logging.debug('Learning: {}'.format(self.get_name()))
        states = sequence.get_sequence()
        features = len(states[0].get_code())
        rv = config["rv"]

        dataset = []
        labels = []

        for state in states:
            dataset.append(state.get_code_rounded(rv))
            labels.append(state.get_best_label()) 

        dataset = np.array(dataset)
        dataset = dataset.reshape((dataset.shape[0], 1, dataset.shape[1]))
        labels = np.array(labels)

        inputs = Input((1, features))
        att_in = LSTM(100, return_sequences=True, dropout=0.5, recurrent_dropout=0.2)(inputs)
        att_out = AttentionLayer()(att_in)
        op = Dense(64, activation='relu', trainable=True)(att_out)
        outputs = Dense(4, activation='softmax', trainable=True)(op)
        self.model = Model(inputs, outputs)
        self.model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        try:
            self.model.fit(x=dataset, y=labels, batch_size=64, epochs=50, verbose=0, shuffle=True, validation_split=0.2)
            logging.info("Attention Analyzer is generated")

            for layer in self.model.layers:
                weights = layer.get_weights()
                #print ("layer: {}, weights: {}".format(layer, weights))
        except:
            self.model = None
            logging.info("Attention Analyzer is not generated")

    def analysis(self, sequence, config):
        logging.debug('Analysis: {}'.format(self.get_name()))

        max_len = config["max_len"]
        rv = config["rv"]
        states = sequence.get_sequence()

        test = []
        for state in states:
            test.append(state.get_code_rounded(rv))
        test = np.array(test)
        test = test.reshape((test.shape[0], 1, test.shape[1]))

        predictions = self.model.predict(test)
        output = tf.cast(tf.argmax(predictions, axis=-1), tf.int32)

        ret = []
        for i in range(len(output)):
            states[i].set_hidden_label_int(output[i])
            if output[i] == 2:
                prob = predictions[i][2]
                ret.append((prob, states[i]))

        self.print_infection_information(ret, config)

        return ret

class AttentionLayer(Layer):
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)

    def build(self, input_shape):
        self.W = self.add_weight(name="att_weight", shape=(input_shape[-1],1), initializer="normal")
        self.b = self.add_weight(name="att_bias", shape=(input_shape[1],1), initializer="zeros")
        super(AttentionLayer, self).build(input_shape)

    def call(self, x):
        et = K.squeeze(K.dot(x, self.W) + self.b, axis=-1)
        #print ("Et size: {}".format(K.int_shape(et)))
        #K.print_tensor(et, message="Et in Attention = ")
        at = K.softmax(et)
        #print ("At size: {}".format(K.int_shape(at)))
        #K.print_tensor(at, message="At in Attention = ")
        at = K.expand_dims(at, axis=-1)
        output = x * at
        #print ("Output size: {}".format(K.int_shape(output)))
        #K.print_tensor(output, message="Output in Attention = ")
        return K.sum(output, axis=1)

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[-1])

    def get_config(self):
        return super(attention, self).get_config()
