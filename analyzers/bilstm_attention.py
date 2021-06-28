import sys
import logging
from analyzers.analyzer import Analyzer
from keras import Input, Model
from keras.layers import Dense, Bidirectional, LSTM, Concatenate, Dropout
from keras import optimizers
import tensorflow as tf
import numpy as np

class BilstmAttention(Analyzer):
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
        lstm = Bidirectional(LSTM(100, dropout=0.5, return_sequences=True))(inputs)
        lstm, forward_h, forward_c, backward_h, backward_c = Bidirectional(LSTM(64, dropout=0.5, return_sequences=True, return_state=True))(lstm)
        state_h = Concatenate()([forward_h, backward_h])
        state_c = Concatenate()([forward_c, backward_c])

        attention = BahdanauAttention(64)
        context_vector, attention_weights = attention(lstm, state_h)

        dense1 = Dense(64, activation="relu")(context_vector)
        output = Dense(4, activation="softmax", trainable=True)(dense1)
        self.model = Model(inputs=inputs, outputs=output)
        self.model.compile(loss="sparse_categorical_crossentropy", optimizer="adam", metrics=["accuracy"])

        try:
            self.model.fit(x=dataset, y=labels, batch_size=64, epochs=50)
            logging.info("BiLSTM Attention Analyzer is generated")
        except:
            self.model = None
            logging.info("BiLSTM Attention Analyzer is not generated")

    def analysis(self, sequence, config):
        logging.debug('Analysis: {}'.format(self.get_name()))
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

class BahdanauAttention(Model):
    def __init__(self, units):
        super(BahdanauAttention, self).__init__()
        self.W1 = Dense(units)
        self.W2 = Dense(units)
        self.V = Dense(1)

    def call(self, values, query):
        hidden_with_time_axis = tf.expand_dims(query, 1)
        score = self.V(tf.nn.tanh(self.W1(values) + self.W2(hidden_with_time_axis)))

        attention_weights = tf.nn.softmax(score, axis=1)

        context_vector = attention_weights * values
        context_vector = tf.reduce_sum(context_vector, axis=1)

        return context_vector, attention_weights
