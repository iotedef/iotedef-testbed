import sys
import logging
from analyzers.analyzer import Analyzer

import numpy as np
from tensorflow.keras.optimizers import Adam
import keras
from keras.models import Sequential, Model, load_model
from keras.layers import LSTM, Dense, RepeatVector, TimeDistributed, Input, BatchNormalization, Activation, dot, concatenate
from keras.callbacks import EarlyStopping

from math import floor, ceil

N_HIDDEN=128
EPOCH=30
THRESHOLD=0.01

class Seq2seqAttention(Analyzer):
    def __init__(self, name):
        super().__init__(name)

    def truncate(self, x, y, slen=100):
        in_, out_ = [], []
        for i in range(len(x) - slen + 1):
            in_.append(x[i:(i+slen)])
            out_.append(y[i:(i+slen)])
        return np.array(in_), np.array(out_)

    def probability_based_embedding(self, p, d):
        ret = 0
        pr = {}

        tmp = zip(range(4), p)
        order = [k for k, _ in sorted(tmp, key=lambda x: x[1], reverse=True)]

        ru = 0
        rd = 0
        for i in range(4):
            r = round(p[i], d)
            c = ceil(p[i] * 10 ** d) / 10 ** d
            f = floor(p[i] * 10 ** d) / 10 ** d
            if r - c == 0:
                ru += 1
            elif r - f == 0:
                rd += 1

        lst = []
        if ru >= 2:
            for i in range(4):
                if i == order[-1]:
                    lst.append(floor(p[i] * 10 ** d) / 10 ** d)
                else:
                    lst.append(round(p[i], d))
            if sum(lst) > 0.999 and sum(lst) < 1.001:
                for i in range(4):
                    pr[i] = lst[i]
            else:
                for i in range(4):
                    if i == order[-1] or i == order[-2]:
                        pr[i] = floor(p[i] * 10 ** d) / 10 ** d
                    else:
                        pr[i] = round(p[i], d)

        elif rd >= 2:
            for i in range(4):
                if i == order[0]:
                    lst.append(ceil(p[i] * 10 ** d) / 10 ** d)
                else:
                    lst.append(round(p[i], d))
            if sum(lst) > 0.999 and sum(lst) < 1.001:
                for i in range(4):
                    pr[i] = lst[i]
            else:
                for i in range(4):
                    if i == order[0] or i == order[1]:
                        pr[i] = ceil(p[i] * 10 ** d) / 10 ** d
                    else:
                        pr[i] = round(p[i], d)

        for i in [2, 1, 0, 3]:
            ret *= 10 ** d
            ret += round(pr[i] * (10 ** d), 0)
        
        return ret

    # Please implement the following functions
    def learning(self, sequence, config):
        logging.debug('Learning: {}'.format(self.get_name()))
        states = sequence.get_sequence()
        features = len(states[0].get_code())
        slen = config["sequence_length"]
        rv = config["rv"]

        in_, out_ = [], []
        idx = 0
        for state in states:
            prob = state.get_probability_vector()
            p = self.probability_based_embedding(prob, rv)
            label = state.get_label("infection")
            logging.info("{}> {} : {}".format(idx, p, label))
            in_.append([p, idx])
            out_.append([label, idx])
            idx += 1

        X_in, X_out = self.truncate(in_, out_, slen=slen)

        input_train = Input(shape=(X_in.shape[1], X_in.shape[2]-1))
        output_train = Input(shape=(X_out.shape[1], X_out.shape[2]-1))

        encoder_stack_h, encoder_last_h, encoder_last_c = LSTM(
                N_HIDDEN, activation='relu', dropout=0.2, recurrent_dropout=0.2,
                return_sequences=True, return_state=True)(input_train)

        encoder_last_h = BatchNormalization(momentum=0.6)(encoder_last_h)
        encoder_last_c = BatchNormalization(momentum=0.6)(encoder_last_c)

        decoder_input = RepeatVector(output_train.shape[1])(encoder_last_h)
        decoder_stack_h = LSTM(N_HIDDEN, activation='relu', dropout=0.2, recurrent_dropout=0.2,
                return_state=False, return_sequences=True)(decoder_input, initial_state=[encoder_last_h, encoder_last_c])

        attention = dot([decoder_stack_h, encoder_stack_h], axes=[2,2])
        attention = Activation('softmax')(attention)

        context = dot([attention, encoder_stack_h], axes=[2,1])
        context = BatchNormalization(momentum=0.6)(context)

        decoder_combined_context = concatenate([context, decoder_stack_h])
        out = TimeDistributed(Dense(output_train.shape[2]))(decoder_combined_context)

        self.model = Model(inputs=input_train, outputs=out)
        opt = Adam(learning_rate=0.01, clipnorm=1)
        self.model.compile(loss='mean_squared_error', optimizer=opt, metrics=['accuracy'])
        #self.model.summary()

        es = EarlyStopping(monitor='val_loss', mode='min', patience=50)
        history = self.model.fit(X_in[:, :, :1], X_out[:, :, :1], validation_split=0.2, epochs=EPOCH, verbose=1, callbacks=[es], batch_size=100)

    def analysis(self, sequence, config):
        logging.debug('Analysis: {}'.format(self.get_name()))
        states = sequence.get_sequence()
        features = len(states[0].get_code())
        slen = config["sequence_length"]
        rv = config["rv"]

        in_ = []
        idx = 0
        for state in states:
            prob = state.get_probability_vector()
            p = self.probability_based_embedding(prob, rv)
            in_.append([p, idx])
            idx += 1

        X_in, _ = self.truncate(in_, in_, slen=slen)
        y_pred = self.model.predict(X_in[:, :, :1])

        idx = 0
        prediction_1 = []
        prediction_0 = []
        predictions = {}
        for pred in y_pred:
            if states[idx].get_label("infection") == 1:
                prediction_1.append(pred[0][0])
            else:
                prediction_0.append(pred[0][0])

            if len(y_pred) - idx > slen:
                lst = range(len(pred))
            else:
                lst = range(len(y_pred)-idx)
            for i in lst:
                if idx + i not in predictions:
                    predictions[idx + i] = []
                predictions[idx + i].append(pred[i][0])
            idx += 1
        results = []
        for idx in range(len(states) - slen + 1):
            res = sum(predictions[idx])/len(predictions[idx])
            results.append(res)

        ret = []
        for idx in range(len(results)):
            states[idx].set_hidden_label_int(0)
            if results[idx] > THRESHOLD:
                states[idx].set_hidden_label_int(1)
                prob = results[idx]
                ret.append((prob, states[idx]))

        self.print_infection_information(ret, config)

        return ret
