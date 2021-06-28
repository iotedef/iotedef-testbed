from definitions.window import Window
import logging
import copy
import time

class TrainingSet:
    def __init__(self):
        self.windows = []
        self.revised = {}

    def add_window(self, window):
        self.windows.append(window)

    def get_windows(self):
        return self.windows

    def get_windows_length(self):
        return len(self.windows)

    def get_feature_names(self):
        ret = None
        if len(self.windows) > 0:
            ret = self.windows[0].get_feature_names()
        return ret

    def get_dataset(self, kind=None):
        dataset = []
        benign = []
        anomalous = []
        
        for w in reversed(self.windows):
            if w.get_window_start_time() == None and w.get_window_end_time() == None:
                self.windows.remove(w)
            else:
                break

        if kind:
            for w in self.windows:
                if w.get_label(kind) == 1:
                    anomalous.append(w)
                else:
                    benign.append(w)

            blen = len(benign)
            alen = len(anomalous)

            if blen > alen:
                clen = blen - alen
                left = clen
                tmp = copy.deepcopy(anomalous)

                while left > 0:
                    logging.info("{} (benign) : {} (anomalous ({})), left: {}".format(len(benign), len(anomalous), kind, left))

                    if left > alen:
                        anomalous += copy.deepcopy(tmp)
                        left -= alen
                    else:
                        anomalous += copy.deepcopy(tmp[:left])
                        left -= left
            else:
                clen = alen - blen
                left = clen
                tmp = copy.deepcopy(benign)

                while left > 0:
                    logging.info("{} (benign) : {} (anomalous ({}))".format(len(benign), len(anomalous), kind))

                    if left > blen:
                        benign = benign + copy.deepcopy(tmp)
                        left -= blen
                    else:
                        benign = benign + copy.deepcopy(tmp[:left])
                        left -= left
                   
            logging.info("final ratio ({}) - {} (benign) : {} (anomalous ({}))".format(kind, len(benign), len(anomalous), kind))
            self.revised[kind] = benign + anomalous
            for w in self.revised[kind]:
                dataset += w.get_code()

        else:
            for w in self.windows:
                dataset += w.get_code()

        return dataset

    def get_num_of_types(self, kind):
        num = 0
        for w in self.windows:
            if w.get_label(kind) == 1:
                num += 1
        return num

    def get_labels(self, kind):
        labels = []

        if kind in self.revised:
            for w in self.revised[kind]:
                labels.append(w.get_label(kind))
        else:
            for w in self.windows:
                labels.append(w.get_label(kind))
        return labels

    def print(self):
        print (">>>>> Windows Information <<<<<")
        for w in self.windows:
            #print ("{}) {}".format(w.get_serial_number(), w.get_code()))
            print ("{}) Window Start Time: {} / Window End Time: {} / Packets in Window (Forward): {} / Packets in Window (Backward): {}".format(w.get_serial_number(), w.get_window_start_time(), w.get_window_end_time(), w.get_num_of_packets("forward"), w.get_num_of_packets("backward")))

    def store(self, sfname, training):
        with open(sfname, "w") as of:
            windows = self.get_windows()
            if training:
                windows = balancing(windows)
            fnames = windows[0].get_feature_names()

            for f in fnames[:-1]:
                of.write("{}, ".format(f))
            of.write("{}: start_time, end_time: label\n".format(fnames[-1]))

            for w in windows:
                [code] = w.get_code()
                start_time = w.get_window_start_time()
                end_time = w.get_window_end_time()

                for c in code[:-1]:
                    of.write("{}, ".format(c))
                of.write("{}".format(code[-1]))
                label = w.get_label()
                of.write(": {}, {}: {}\n".format(start_time, end_time, label))

def balancing(windows):
    num = {}
    num[0] = 0 # benign
    num[1] = 0 # attack
    num[2] = 0 # infection
    num[3] = 0 # reconnaissance

    for w in windows:
        label = w.get_best_label()
        num[label] += 1

    if num[0] == 0 or num[1] == 0 or num[2] == 0 or num[3] == 0:
        logging.error("The training set should be replayed: benign: {} / attack: {} / infection: {} / reconnaissance: {}".format(num[0], num[1], num[2], num[3]))
        sys.exit(1)

    mval = num[0]
    for i in range(4):
        if mval < num[i]:
            mval = num[i]

    win = {}
    left = {}

    for i in range(4):
        win[i] = []
        left[i] = mval - num[i]

    while left[0] > 0 or left[1] > 0 or left[2] > 0 or left[3] > 0:
        for w in windows:
            label = w.get_best_label()

            if left[label] > 0:
                if left[label] < num[label]:
                    coin = random.random()
                    if coin < 0.7:
                        win[label].append(copy.deepcopy(w))
                        left[label] -= 1
                else:
                    win[label].append(copy.deepcopy(w))
                    left[label] -= 1

    windows = windows + win[0] + win[1] + win[2] + win[3]
    windows = sorted(windows, key=lambda x: x.get_window_start_time())

    revised = {}
    for i in range(4):
        revised[i] = 0

    for w in windows:
        label = w.get_best_label()
        revised[label] += 1

    logging.info("Revised number of samples: benign: {}, attack: {}, infection: {}, reconnaissance: {}".format(revised[0], revised[1], revised[2], revised[3]))
    return windows

