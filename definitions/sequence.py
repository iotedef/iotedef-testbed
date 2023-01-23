from definitions.batch import Batch
import copy
import random
import logging
import time

class Sequence():
    def __init__(self, sequence, start, end, granularity=0.01, width=100):
        #self.sequence = copy.deepcopy(sequence)
        self.sequence = sequence
        self.start_time = start
        self.end_time = end
        self.granularity = granularity
        self.batches = []

        first_end = self.start_time + self.granularity
        first_start = first_end - width * granularity

        last_start = self.end_time
        last_end = last_start + width * granularity

        for i in self.drange(first_start, last_start + self.granularity, self.granularity):
            start = i
            end = i + width * granularity
            b = []

            for state in self.sequence:
                if state.get_start_time() >= start and state.get_end_time() < end:
                    b.append(state)
            self.batches.append(Batch(b, start, width, granularity))

    def get_sequence(self):
        return self.sequence

    def get_sequence_length(self):
        return len(self.sequence)

    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time

    def get_batches(self):
        return self.batches

    def store(self, ofname, training):
        fnames = self.sequence[0].get_feature_names()
        #if training:
        #    self.sequence = balancing(self.sequence)
        #self.sequence = sorted(self.sequence, key=lambda x: x.get_start_time())
        logging.info(">>> Before opening {}".format(ofname))
        with open(ofname, "w") as of:
            of.write("flow_info: ")
            for f in fnames[:-1]:
                of.write("{}, ".format(f))
            of.write("{}: serial: start_time, end_time: attack_label: infection_label: reconnaissance_label: attack_labeled: infection_labeled: reconnaissance_labeled: benign_probability: attack_probability: infection_probability: reconnaissance_probability\n".format(fnames[-1]))

            for state in self.sequence:
                of.write("{}: ".format(state.get_flow_info().replace(":", "/")))
                for f in fnames[:-1]:
                    of.write("{}, ".format(state.get_feature_value(f)))
                of.write("{}: {}: {}, {}: {}: {}: {}: {}: {}: {}: {}: {}: {}: {}\n".format(state.get_feature_value(fnames[-1]), state.get_serial_number(), state.get_start_time(), state.get_end_time(), state.get_label("attack"), state.get_label("infection"), state.get_label("reconnaissance"), state.get_labeled("attack"), state.get_labeled("infection"), state.get_labeled("reconnaissance"), state.get_probability("benign"), state.get_probability("attack"), state.get_probability("infection"), state.get_probability("reconnaissance")))
        logging.info(">>> After storing the sequence at {}".format(ofname))

    def print_sequence(self):
        print ("Start time: {}".format(self.start_time))
        print ("End time: {}".format(self.end_time))
        print ("# of States in Sequence: {}".format(len(self.sequence)))
        
        for s in self.sequence:
            print ("<{}-{}> [{}] attack: {} ({}), infection: {} ({}), reconnaissance: {} ({})".format(s.get_start_time(), s.get_end_time(), s.get_best_label(), s.get_label("attack"), s.get_probability("attack"), s.get_label("infection"), s.get_probability("infection"), s.get_label("reconnaissance"), s.get_probability("reconnaissance")))

    def drange(self, start, stop, step=1):
        n = int(round((stop - start)/float(step)))
        if n > 1:
            return [start + step * i for i in range(n + 1)]
        elif n == 1:
            return [start]
        else:
            return []

    def get_granularity(self):
        return self.granularity

    def get_events_at(self, time):
        ret = []
        for state in self.sequence:
            if state.get_start_time() == time:
                ret.append(state)
        return ret

def balancing(sequence):
    num = {}
    num[0] = 0 # benign
    num[1] = 0 # attack
    num[2] = 0 # infection
    num[3] = 0 # reconnaissance

    for s in sequence:
        label = s.get_best_label()
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
        for s in sequence:
            label = s.get_best_label()

            if left[label] > 0:
                if left[label] < num[label]:
                    coin = random.random()
                    if coin < 0.7:
                        win[label].append(copy.deepcopy(s))
                        left[label] -= 1
                else:
                    win[label].append(copy.deepcopy(s))
                    left[label] -= 1

    sequence = sequence + win[0] + win[1] + win[2] + win[3]
    sequence = sorted(sequence, key=lambda x: x.get_start_time())

    revised = {}
    for i in range(4):
        revised[i] = 0

    for s in sequence:
        label = s.get_best_label()
        revised[label] += 1

    logging.info("Revised number of samples: benign: {}, attack: {}, infection: {}, reconnaissance: {}".format(revised[0], revised[1], revised[2], revised[3]))
    return sequence

