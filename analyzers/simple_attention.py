import sys
import logging
import numpy as np
from analyzers.analyzer import Analyzer
from keras import Input, Model
from keras.layers import LSTM, Dense, Layer
from keras.regularizers import l2
import keras.backend as K
import tensorflow as tf

class SimpleAttention(Analyzer):
    def __init__(self, name):
        super().__init__(name)

    # Please implement the following functions
    def learning(self, sequence, config):
        logging.debug('Learning: {}'.format(self.get_name()))
        states = sequence.get_sequence()
        rv = config["rv"]

        dataset = []
        labels = []

        for state in states:
            data = state.get_best_label()
            dataset.append([data])
            label = data
            labels.append(label)

        dataset = np.array(dataset)
        print ("dataset: {}".format(dataset))
        print ("dataset.shape: {}".format(dataset.shape))
        dataset = dataset.reshape((dataset.shape[0], 1, dataset.shape[1]))
        labels = np.array(labels)

        inputs = Input((1, 1))
        att_in = LSTM(100, return_sequences=True, dropout=0.5, recurrent_dropout=0.2)(inputs)
        att_out = AttentionLayer()(att_in)
        op = Dense(64, activation='relu', trainable=True)(att_out)
        outputs = Dense(4, activation='softmax', trainable=True)(op)
        self.model = Model(inputs, outputs)
        self.model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

        try:
            self.model.fit(x=dataset, y=labels, batch_size=64, epochs=50, verbose=1, shuffle=True, validation_split=0.2)
            logging.info("Attention Analyzer is generated")
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
            test.append([state.get_best_label()])
        test = np.array(test)
        test = test.reshape((test.shape[0], 1, test.shape[1]))

        predictions = self.model.predict(test)
        print ("predictions: {}".format(predictions))
        output = tf.cast(tf.argmax(predictions, axis=-1), tf.int32)
        print ("output: {}".format(output))

        ret = []
        for i in range(len(output)):
            states[i].set_hidden_label_int(output[i])
            if output[i] == 2:
                prob = predictions[i][2]
                ret.append((prob, states[i]))

        self.print_infection_information(ret)

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
        logging.info("Et in Attention: {}".format(et))
        at = K.softmax(et)
        logging.info("At in Attention: {}".format(at))
        at = K.expand_dims(at, axis=-1)
        output = x * at
        logging.info("Output in Attention: {}".format(output))
        return K.sum(output, axis=1)

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[-1])

    def get_config(self):
        return super(attention, self).get_config()

def dot_product(query, key, value):
    matmul_qk = tf.matmul(query, key, transpose_b=True)
    attention_weights = tf.nn.softmax(matmul_qk, axis=-1)
    output = tf.matmul(attention_weights, value)

    return output, attention_weights
