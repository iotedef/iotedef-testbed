import sys
import logging
from analyzers.analyzer import Analyzer

import numpy as np
from tensorflow.keras.optimizers import Adam
import keras
from keras.models import Sequential, Model, load_model
from keras.layers import LSTM, Dense, RepeatVector, TimeDistributed, Input, BatchNormalization, Activation, dot, concatenate
from keras.callbacks import EarlyStopping

N_HIDDEN=128
EPOCH=10

class Seq2seqAttention(Analyzer):
    def __init__(self, name):
        super().__init__(name)

    def truncate(self, x, y, slen=100):
        in_, out_ = [], []
        for i in range(len(x) - slen + 1):
            in_.append(x[i:(i+slen)])
            out_.append(y[i:(i+slen)])
        return np.array(in_), np.array(out_)

    # Please implement the following functions
    def learning(self, sequence, config):
        logging.debug('Learning: {}'.format(self.get_name()))
        states = sequence.get_sequence()
        features = len(states[0].get_code())
        slen = config["sequence_length"]

        logging.info("len(states): {}".format(len(states)))
        logging.info("slen: {}".format(slen))
        idx = 0

        in_, out_ = [], []
        for state in states:
            prob = state.get_probability_vector()
            p = prob[0] * 1 + prob[1] * 2 + prob[2] * 3 + prob[3] * 4
            #label = state.get_label_vector()
            label = state.get_best_label()
            in_.append([p, idx])
            out_.append([label, idx])
            idx += 1

        X_in, X_out = self.truncate(in_, out_, slen=slen)

        logging.info("X_in.shape: {}".format(X_in.shape))
        logging.info("X_out.shape: {}".format(X_out.shape))

        input_train = Input(shape=(X_in.shape[1], X_in.shape[2]-1))
        output_train = Input(shape=(X_out.shape[1], X_out.shape[2]-1))

        encoder_stack_h, encoder_last_h, encoder_last_c = LSTM(
                N_HIDDEN, activation='elu', dropout=0.2, recurrent_dropout=0.2,
                return_sequences=True, return_state=True)(input_train)

        encoder_last_h = BatchNormalization(momentum=0.6)(encoder_last_h)
        encoder_last_c = BatchNormalization(momentum=0.6)(encoder_last_c)

        decoder_input = RepeatVector(output_train.shape[1])(encoder_last_h)
        decoder_stack_h = LSTM(N_HIDDEN, activation='elu', dropout=0.2, recurrent_dropout=0.2,
                return_state=False, return_sequences=True)(decoder_input, initial_state=[encoder_last_h, encoder_last_c])

        attention = dot([decoder_stack_h, encoder_stack_h], axes=[2,2])
        attention = Activation('softmax')(attention)

        context = dot([attention, encoder_stack_h], axes=[2,1])
        context = BatchNormalization(momentum=0.6)(context)

        decoder_combined_context = concatenate([context, decoder_stack_h])
        out = TimeDistributed(Dense(output_train.shape[2]))(decoder_combined_context)

        self.model = Model(inputs=input_train, outputs=out)
        opt = Adam(learning_rate=0.01, clipnorm=1)
        self.model.compile(loss='mean_squared_error', optimizer=opt, metrics=['mae'])
        self.model.summary()

        es = EarlyStopping(monitor='val_loss', mode='min', patience=50)
        history = self.model.fit(X_in[:, :, :1], X_out[:, :, :1], validation_split=0.2, epochs=EPOCH, verbose=1, callbacks=[es], batch_size=100)

    def analysis(self, sequence, config):
        logging.debug('Analysis: {}'.format(self.get_name()))
        states = sequence.get_sequence()
        features = len(states[0].get_code())
        slen = config["sequence_length"]

        logging.info("len(states): {}".format(len(states)))
        logging.info("slen: {}".format(slen))
        idx = 0

        in_ = []
        for state in states:
            prob = state.get_probability_vector()
            p = prob[0] * 1 + prob[1] * 2 + prob[2] * 3 + prob[3] * 4
            in_.append([p, idx])
            idx += 1

        X_in, _ = self.truncate(in_, in_, slen=slen)
        y_pred = self.model.predict(X_in[:, :, :1])

        logging.info("len(X_in): {}".format(len(X_in)))
        logging.info("len(y_pred): {}".format(len(y_pred)))

