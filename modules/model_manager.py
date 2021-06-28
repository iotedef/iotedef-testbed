import argparse
import time
import logging
import threading
import copy
import sys
import asyncio
sys.path.append("..")
from utils.autils import init_algorithms
from definitions.training_set import TrainingSet
from sklearn import metrics

usleep = lambda x: time.sleep(x/1000000.0)
THREAD_USLEEP_TIME = 30000
WAITING_USLEEP_TIME = 10000
PROCESS_TIMEOUT = 3/1000000.0
OFFSET = 0.2

class ModelManager:
    def __init__(self, core, anames, inames, rnames, strategy=1):
        self.core = core
        self.anames = anames
        self.inames = inames
        self.rnames = rnames
        self.algorithms = {}
        self.training_set = TrainingSet()
        self.is_model_generated = False
        self.is_test_finished = False
        self.is_learning_invoked = False
        self.is_evolve_finished = False
        self.is_retest_finished = False
        self.strategy = strategy

        self.queue = []
        self.cnt = 1
        self.acnt = 0

        self.infection_labeled_windows = []

        self.training_packets = 0
        self.test_packets = 0
        self.retest_packets = 0
    
        self.test_labels = {}
        self.test_labels["attack"] = []
        self.test_labels["infection"] = []
        self.test_labels["reconnaissance"] = []
        self.test_labels["evolution"] = []

        self.predicted_labels = {}
        self.predicted_labels["attack"] = {}
        self.predicted_labels["infection"] = {}
        self.predicted_labels["reconnaissance"] = {}
        self.predicted_labels["evolution"] = {}

        self.accuracy = {}
        self.accuracy["attack"] = {}
        self.accuracy["infection"] = {}
        self.accuracy["reconnaissance"] = {}
        self.accuracy["evolution"] = {}

        self.precision = {}
        self.precision["attack"] = {}
        self.precision["infection"] = {}
        self.precision["reconnaissance"] = {}
        self.precision["evolution"] = {}

        self.recall = {}
        self.recall["attack"] = {}
        self.recall["infection"] = {}
        self.recall["reconnaissance"] = {}
        self.recall["evolution"] = {}

        self.f1 = {}
        self.f1["attack"] = {}
        self.f1["infection"] = {}
        self.f1["reconnaissance"] = {}
        self.f1["evolution"] = {}

        self.auc = {}
        self.auc["attack"] = {}
        self.auc["infection"] = {}
        self.auc["reconnaissance"] = {}
        self.auc["evolution"] = {}

        self.learning_time = {}
        self.learning_time["attack"] = {}
        self.learning_time["infection"] = {}
        self.learning_time["reconnaissance"] = {}
        self.learning_time["evolution"] = {}

        self.first_detection_time = {}
        self.first_detection_time["attack"] = {}
        self.first_detection_time["infection"] = {}
        self.first_detection_time["reconnaissance"] = {}
        self.first_detection_time["evolution"] = {}

        self.attack_start_time = None
        self.infection_start_time = None
        self.reconnaissance_start_time = None

        init_algorithms(self)
        self.num_of_attack_windows = 0
        self.num_of_infection_windows = 0
        self.num_of_reconnaissance_windows = 0
        self.num_of_einfection_windows = 0
        self.num_of_benign_windows = 0
        self.num_of_ebenign_windows = 0

        self.true_positive = {}
        self.true_positive["attack"] = {}
        self.true_positive["infection"] = {}
        self.true_positive["reconnaissance"] = {}
        self.true_positive["evolution"] = {}

        self.true_negative = {}
        self.true_negative["attack"] = {}
        self.true_negative["infection"] = {}
        self.true_negative["reconnaissance"] = {}
        self.true_negative["evolution"] = {}

        self.false_positive = {}
        self.false_positive["attack"] = {}
        self.false_positive["infection"] = {}
        self.false_positive["reconnaissance"] = {}
        self.false_positive["evolution"] = {}

        self.false_negative = {}
        self.false_negative["attack"] = {}
        self.false_negative["infection"] = {}
        self.false_negative["reconnaissance"] = {}
        self.false_negative["evolution"] = {}

        for aname in anames:
            if aname not in self.algorithms:
                logging.error("Initializing ModelManager error: No algorithm exists: {}".format(aname))
                sys.exit(1)
            self.predicted_labels["attack"][aname] = []
            self.accuracy["attack"][aname] = None
            self.precision["attack"][aname] = None
            self.recall["attack"][aname] = None
            self.f1["attack"][aname] = None
            self.auc["attack"][aname] = None
            self.learning_time["attack"][aname] = None
            self.first_detection_time["attack"][aname] = None
            self.true_positive["attack"][aname] = 0
            self.true_negative["attack"][aname] = 0
            self.false_positive["attack"][aname] = 0
            self.false_negative["attack"][aname] = 0
    
        for iname in inames:
            if iname not in self.algorithms:
                logging.error("Initializing ModelManager error: No algorithm exists: {}".format(iname))
                sys.exit(1)
            self.predicted_labels["infection"][iname] = []
            self.accuracy["infection"][iname] = None
            self.precision["infection"][iname] = None
            self.recall["infection"][iname] = None
            self.f1["infection"][iname] = None
            self.auc["infection"][iname] = None
            self.learning_time["infection"][iname] = None
            self.first_detection_time["infection"][iname] = None
            self.true_positive["infection"][iname] = 0
            self.true_negative["infection"][iname] = 0
            self.false_positive["infection"][iname] = 0
            self.false_negative["infection"][iname] = 0

            self.predicted_labels["evolution"][iname] = []
            self.accuracy["evolution"][iname] = None
            self.precision["evolution"][iname] = None
            self.recall["evolution"][iname] = None
            self.f1["evolution"][iname] = None
            self.auc["evolution"][iname] = None
            self.learning_time["evolution"][iname] = None
            self.first_detection_time["evolution"][iname] = None
            self.true_positive["evolution"][iname] = 0
            self.true_negative["evolution"][iname] = 0
            self.false_positive["evolution"][iname] = 0
            self.false_negative["evolution"][iname] = 0

        for rname in rnames:
            if rname not in self.algorithms:
                logging.error("Initializing ModelManager error: No algorithm exists: {}".format(rname))
                sys.exit(1)
            self.predicted_labels["reconnaissance"][rname] = []
            self.accuracy["reconnaissance"][rname] = None
            self.precision["reconnaissance"][rname] = None
            self.recall["reconnaissance"][rname] = None
            self.f1["reconnaissance"][rname] = None
            self.auc["reconnaissance"][rname] = None
            self.learning_time["reconnaissance"][rname] = None
            self.first_detection_time["reconnaissance"][rname] = None
            self.true_positive["reconnaissance"][rname] = 0
            self.true_negative["reconnaissance"][rname] = 0
            self.false_positive["reconnaissance"][rname] = 0
            self.false_negative["reconnaissance"][rname] = 0

        loop = asyncio.new_event_loop()
        mm = threading.Thread(target=run, args=(self, loop,), daemon=True)
        mm.start()

    def add_window(self, window):
        self.queue.append(window)

    def add_algorithm(self, algorithm):
        self.algorithms[algorithm.get_name()] = algorithm
        logging.debug("Algorithm {} is loaded".format(algorithm.get_name()))

    def get_queue_length(self):
        return len(self.queue)

    def get_is_model_generated(self):
        return self.is_model_generated

    def get_is_test_finished(self):
        return self.is_test_finished

    def get_is_retest_finished(self):
        return self.is_retest_finished

    def get_is_evolve_finished(self):
        return self.is_evolve_finished

    def get_cnt(self):
        return self.cnt

    def get_acnt(self):
        return self.acnt

    def get_training_set(self):
        return self.training_set

    def update_model(self, serials):
        windows = self.infection_labeled_windows
        logging.info("# of infection_labeled_windows: {}".format(len(windows)))
        
        before = self.training_set.get_windows_length()
        for window in windows:
            serial = window.get_serial_number()

            if self.strategy == 1:
                logging.info("Strategy 1 works")
                if serial in serials:
                    window.set_label("infection", 1)
                else:
                    window.set_label("infection", 0)
            elif self.strategy == 2:
                logging.info("Strategy 2 works")
                if serial in serials:
                    window.set_label("infection", 1)
            elif self.strategy == 3:
                logging.info("Strategy 3 works")
                if serial not in serials:
                    window.set_label("infection", 0)

            self.training_set.add_window(window)
        after = self.training_set.get_windows_length()
        logging.info("before # of windows: {}, after # of windows: {}".format(before, after))
        if self.inames:
            for iname in self.inames:
                before = time.time()
                self.algorithms[iname].learning(self.training_set, "infection")
                after = time.time()
                self.learning_time["evolution"][iname] = after - before
   
        self.is_evolve_finished = True

    async def learning(self, window):
        if window:
            self.training_packets += window.get_num_of_packets("both")
            logging.debug("Receive one Window in the learning phase: {}".format(window.get_code()))
            #logging.info("Model Manager (in)> {}) {}: Window Start Time: {} / Window End Time: {} / Packets in Window (Forward): {} / Packets in Window (Backward): {}".format(window.get_serial_number(), window.get_flow_info("forward"), window.get_window_start_time(), window.get_window_end_time(), window.get_num_of_packets("forward"), window.get_num_of_packets("backward")))
            logging.debug("model_manager> Window's label in ModelManager (Attack Label: {}, Infection Label: {}, Reconnaissance: {})".format(window.get_label("attack"), window.get_label("infection"), window.get_label("reconnaissance")))

            if window.get_serial_number() != self.cnt:
                logging.error("Inconsistency: Serial Number: {} / Count: {}".format(window.get_serial_number(), self.cnt))
            else:
                self.cnt += 1
                if window.get_label("infection") == 1:
                    self.acnt += 1
 
            self.training_set.add_window(window)

        if self.core.get_is_training_set_processed() and self.is_learning_invoked == False:
            logging.info("Before generating the model based on the training set")
            self.is_learning_invoked = True
            dataset = self.training_set.get_dataset()
            logging.info("# of Samples in Dataset: {}".format(len(dataset)))
            logging.debug("Dataset ({}): {}".format(len(dataset), dataset))

            if self.anames:
                for aname in self.anames:
                    before = time.time()
                    self.algorithms[aname].learning(self.training_set, "attack")
                    after = time.time()
                    self.learning_time["attack"][aname] = after - before

            if self.inames:
                for iname in self.inames:
                    before = time.time()
                    self.algorithms[iname].learning(self.training_set, "infection")
                    after = time.time()
                    self.learning_time["infection"][iname] = after - before

            if self.rnames:
                for rname in self.rnames:
                    before = time.time()
                    self.algorithms[rname].learning(self.training_set, "reconnaissance")
                    after = time.time()
                    self.learning_time["reconnaissance"][rname] = after - before

            self.is_model_generated = True
            logging.info("After generating the model based on the training set")

            self.core.send_training_set_to_sequence_manager(self.training_set)

    async def detection(self, window):
        if window:
            self.test_packets += window.get_num_of_packets("both")
            #logging.info("Detection> {}) {}: Window Start Time: {} / Window End Time: {} / Packets in Window (Forward): {} / Packets in Window (Backward): {}".format(window.get_serial_number(), window.get_flow_info("forward"), window.get_window_start_time(), window.get_window_end_time(), window.get_num_of_packets("forward"), window.get_num_of_packets("backward")))
            curr = time.time()
            self.test_labels["attack"].append(window.get_label("attack"))
            self.test_labels["infection"].append(window.get_label("infection"))
            self.test_labels["reconnaissance"].append(window.get_label("reconnaissance"))

            if window.get_label("attack") == 1:
                self.num_of_attack_windows += 1

            if window.get_label("infection") == 1:
                self.num_of_infection_windows += 1

            if window.get_label("reconnaissance") == 1:
                self.num_of_reconnaissance_windows += 1
            
            if window.get_label("attack") == 0 and window.get_label("infection") == 0 and window.get_label("reconnaissance") == 0:
                self.num_of_benign_windows += 1

            aresult = None
            iresult = None
            rresult = None

            for aname in self.anames:
                aresult, aprob = self.algorithms[aname].detection(window, "attack")
                self.predicted_labels["attack"][aname].append(aresult[0])
                if aresult[0] == 1:
                    logging.debug("{}) The Window is identified as an anomalous one".format(aname))
                    start_time = self.core.get_attack_start_time()
                    if window.get_label("attack") == 1:
                        test_start_time = self.core.get_test_start_time()
                        if start_time and start_time < curr and self.first_detection_time["attack"][aname] == None:
                            self.attack_start_time = start_time - test_start_time
                            logging.debug("curr: {} / test_start_time: {} / self.attack_start_time: {}".format(curr, test_start_time, self.attack_start_time))
                            self.first_detection_time["attack"][aname] = curr - test_start_time - self.attack_start_time


            for iname in self.inames:
                iresult, iprob = self.algorithms[iname].detection(window, "infection")
                self.predicted_labels["infection"][iname].append(iresult[0])

                if iresult[0] == 1:
                    logging.debug("{}) The Window is identified as an infection one".format(iname))
                    start_time = self.core.get_infection_start_time()
                    if window.get_label("infection") == 1:
                        test_start_time = self.core.get_test_start_time()
                        if start_time and start_time < curr and self.first_detection_time["infection"][iname] == None:
                            self.first_detection_time["infection"][iname] = curr - start_time

            for rname in self.rnames:
                rresult, rprob = self.algorithms[rname].detection(window, "reconnaissance")
                self.predicted_labels["reconnaissance"][rname].append(rresult[0])

                if rresult[0] == 1:
                    logging.debug("{}) The Window is identified as an reconnaissance one".format(rname))
                    start_time = self.core.get_reconnaissance_start_time()
                    if window.get_label("reconnaissance") == 1:
                        test_start_time = self.core.get_test_start_time()
                        if start_time and start_time < curr and self.first_detection_time["reconnaissance"][rname] == None:
                            self.first_detection_time["reconnaissance"][rname] = curr - start_time

            wnd = copy.copy(window)
            if aresult:
                wnd.set_labeled("attack", aresult[0])
            if iresult:
                wnd.set_labeled("infection", iresult[0])
            if rresult:
                wnd.set_labeled("reconnaissance", rresult[0])

            aidx = 0
            iidx = 0
            ridx = 0
            if aprob:
                wnd.set_probability("attack", aprob[1])
            if iprob:
                wnd.set_probability("infection", iprob[1])
            if rprob:
                wnd.set_probability("reconnaissance", rprob[1])

            wnd.set_probability_complete()
            if wnd.get_labeled("infection") == 1:
                self.infection_labeled_windows.append(wnd)

            self.core.send_window_to_sequence_manager(wnd)

        if self.core.get_is_test_set_processed():
            for aname in self.anames:
                self.accuracy["attack"][aname] = round(metrics.accuracy_score(self.test_labels["attack"], self.predicted_labels["attack"][aname]), 2)
                self.precision["attack"][aname] = round(metrics.precision_score(self.test_labels["attack"], self.predicted_labels["attack"][aname], zero_division=0), 2)
                self.recall["attack"][aname] = round(metrics.recall_score(self.test_labels["attack"], self.predicted_labels["attack"][aname], zero_division=0), 2)
                self.f1["attack"][aname] = round(metrics.f1_score(self.test_labels["attack"], self.predicted_labels["attack"][aname], zero_division=0), 2)
                try:
                    self.auc["attack"][aname] = round(metrics.roc_auc_score(self.test_labels["attack"], self.predicted_labels["attack"][aname]), 2)
                except:
                    self.auc["attack"][aname] = None

                tp = tn = fp = fn = 0
                labels = len(self.test_labels["attack"])
                ones = zeros = 0
                for i in range(labels):
                    if self.test_labels["attack"][i] == 0:
                        zeros += 1
                        if self.predicted_labels["attack"][aname][i] == 0:
                            tn += 1
                        else:
                            fp += 1
                    else:
                        ones += 1
                        if self.predicted_labels["attack"][aname][i] == 0:
                            fn += 1
                        else:
                            tp += 1

                self.true_positive["attack"][aname] = tp
                self.true_negative["attack"][aname] = tn
                self.false_positive["attack"][aname] = fp
                self.false_negative["attack"][aname] = fn

            for iname in self.inames:
                self.accuracy["infection"][iname] = round(metrics.accuracy_score(self.test_labels["infection"], self.predicted_labels["infection"][iname]), 2)
                self.precision["infection"][iname] = round(metrics.precision_score(self.test_labels["infection"], self.predicted_labels["infection"][iname], zero_division=0), 2)
                self.recall["infection"][iname] = round(metrics.recall_score(self.test_labels["infection"], self.predicted_labels["infection"][iname], zero_division=0), 2)
                self.f1["infection"][iname] = round(metrics.f1_score(self.test_labels["infection"], self.predicted_labels["infection"][iname], zero_division=0), 2)
                try:
                    self.auc["infection"][iname] = round(metrics.roc_auc_score(self.test_labels["infection"], self.predicted_labels["infection"][iname]), 2)
                except:
                    self.auc["infection"][iname] = None

                tp = tn = fp = fn = 0
                labels = len(self.test_labels["infection"])
                ones = zeros = 0
                for i in range(labels):
                    if self.test_labels["infection"][i] == 0:
                        zeros += 1
                        if self.predicted_labels["infection"][iname][i] == 0:
                            tn += 1
                        else:
                            fp += 1
                    else:
                        ones += 1
                        if self.predicted_labels["infection"][iname][i] == 0:
                            fn += 1
                        else:
                            tp += 1

                self.true_positive["infection"][iname] = tp
                self.true_negative["infection"][iname] = tn
                self.false_positive["infection"][iname] = fp
                self.false_negative["infection"][iname] = fn

            for rname in self.rnames:
                self.accuracy["reconnaissance"][rname] = round(metrics.accuracy_score(self.test_labels["reconnaissance"], self.predicted_labels["reconnaissance"][rname]), 2)
                self.precision["reconnaissance"][rname] = round(metrics.precision_score(self.test_labels["reconnaissance"], self.predicted_labels["reconnaissance"][rname], zero_division=0), 2)
                self.recall["reconnaissance"][rname] = round(metrics.recall_score(self.test_labels["reconnaissance"], self.predicted_labels["reconnaissance"][rname], zero_division=0), 2)
                self.f1["reconnaissance"][rname] = round(metrics.f1_score(self.test_labels["reconnaissance"], self.predicted_labels["reconnaissance"][rname], zero_division=0), 2)
                try:
                    self.auc["reconnaissance"][rname] = round(metrics.roc_auc_score(self.test_labels["reconnaissance"], self.predicted_labels["reconnaissance"][rname]), 2)
                except:
                    self.auc["reconnaissance"][rname] = None

                tp = tn = fp = fn = 0
                labels = len(self.test_labels["reconnaissance"])
                ones = zeros = 0
                for i in range(labels):
                    if self.test_labels["reconnaissance"][i] == 0:
                        zeros += 1
                        if self.predicted_labels["reconnaissance"][rname][i] == 0:
                            tn += 1
                        else:
                            fp += 1
                    else:
                        ones += 1
                        if self.predicted_labels["reconnaissance"][rname][i] == 0:
                            fn += 1
                        else:
                            tp += 1

                self.true_positive["reconnaissance"][rname] = tp
                self.true_negative["reconnaissance"][rname] = tn
                self.false_positive["reconnaissance"][rname] = fp
                self.false_negative["reconnaissance"][rname] = fn

            self.is_test_finished = True

    async def redetection(self, window):
        if window:
            self.retest_packets += window.get_num_of_packets("both")
            curr = time.time()
            self.test_labels["evolution"].append(window.get_label("infection"))

            if window.get_label("infection") == 1:
                self.num_of_einfection_windows += 1

            if window.get_label("attack") == 0 and window.get_label("infection") == 0 and window.get_label("reconnaissance") == 0:
                self.num_of_ebenign_windows += 1

            eresult = None

            for iname in self.inames:
                eresult, eprob = self.algorithms[iname].detection(window, "infection")
                self.predicted_labels["evolution"][iname].append(eresult[0])

                if eresult[0] == 1:
                    logging.debug("{}) The Window is identified as an infection one".format(iname))

        if self.core.get_is_retest_set_processed():
            for iname in self.inames:
                self.accuracy["evolution"][iname] = round(metrics.accuracy_score(self.test_labels["evolution"], self.predicted_labels["evolution"][iname]), 2)
                self.precision["evolution"][iname] = round(metrics.precision_score(self.test_labels["evolution"], self.predicted_labels["evolution"][iname], zero_division=0), 2)
                self.recall["evolution"][iname] = round(metrics.recall_score(self.test_labels["evolution"], self.predicted_labels["evolution"][iname], zero_division=0), 2)
                self.f1["evolution"][iname] = round(metrics.f1_score(self.test_labels["evolution"], self.predicted_labels["evolution"][iname], zero_division=0), 2)
                try:
                    self.auc["evolution"][iname] = round(metrics.roc_auc_score(self.test_labels["evolution"], self.predicted_labels["evolution"][iname]), 2)
                except:
                    self.auc["evolution"][iname] = None

                tp = tn = fp = fn = 0
                labels = len(self.test_labels["evolution"])
                ones = zeros = 0
                for i in range(labels):
                    if self.test_labels["evolution"][i] == 0:
                        zeros += 1
                        if self.predicted_labels["evolution"][iname][i] == 0:
                            tn += 1
                        else:
                            fp += 1
                    else:
                        ones += 1
                        if self.predicted_labels["evolution"][iname][i] == 0:
                            fn += 1
                        else:
                            tp += 1

                self.true_positive["evolution"][iname] = tp
                self.true_negative["evolution"][iname] = tn
                self.false_positive["evolution"][iname] = fp
                self.false_negative["evolution"][iname] = fn

            self.is_retest_finished = True

    def get_anames(self):
        return self.anames

    def get_inames(self):
        return self.inames

    def get_rnames(self):
        return self.rnames

    def get_accuracy(self, kind, name):
        return self.accuracy[kind][name]

    def get_precision(self, kind, name):
        return self.precision[kind][name]

    def get_recall(self, kind, name):
        return self.recall[kind][name]

    def get_f1(self, kind, name):
        return self.f1[kind][name]

    def get_tp(self, kind, name):
        return self.true_positive[kind][name]

    def get_tn(self, kind, name):
        return self.true_negative[kind][name]

    def get_fp(self, kind, name):
        return self.false_positive[kind][name]

    def get_fn(self, kind, name):
        return self.false_negative[kind][name]

    def get_auc(self, kind, name):
        return self.auc[kind][name]

    def get_learning_time(self, kind, name):
        return self.learning_time[kind][name]

    def get_first_detection_time(self, kind, name):
        return self.first_detection_time[kind][name]

    def get_num_of_benign_windows(self):
        return self.num_of_benign_windows

    def get_num_of_ebenign_windows(self):
        return self.num_of_ebenign_windows

    def get_num_of_attack_windows(self):
        return self.num_of_attack_windows

    def get_num_of_infection_windows(self):
        return self.num_of_infection_windows

    def get_num_of_einfection_windows(self):
        return self.num_of_einfection_windows

    def get_num_of_reconnaissance_windows(self):
        return self.num_of_reconnaissance_windows

    def print_result(self):
        print (">>> Result of Anomaly Detection <<<")

        idx = 0
        print ("1. Attack")
        for aname in self.anames:
            idx += 1
            print ("{}) {}".format(idx, aname))
            print ("  - Accuracy: {}".format(self.accuracy["attack"][aname]))
            print ("  - Precision: {}".format(self.precision["attack"][aname]))
            print ("  - Recall: {}".format(self.recall["attack"][aname]))
            print ("  - F1: {}".format(self.f1["attack"][aname]))
            print ("  - ROC AUC: {}".format(self.auc["attack"][aname]))
            print ("  - # of Training Samples: {}".format(len(self.training_set.get_dataset())))
            print ("  - # of Training Attack Samples: {}".format(self.training_set.get_num_of_types("attack")))
            print ("  - # of Training Packets: {}".format(self.training_packets))
            print ("  - # of Test Samples: {}".format(len(self.test_labels["attack"])))
            print ("  - # of Test Packets: {}".format(self.test_packets))
            print ("    # of benign windows: {}".format(self.num_of_benign_windows))
            print ("    # of attack windows: {}".format(self.num_of_attack_windows))
            print ("  - True Positive: {}".format(self.true_positive["attack"][aname]))
            print ("  - True Negative: {}".format(self.true_negative["attack"][aname]))
            print ("  - False Positive: {}".format(self.false_positive["attack"][aname]))
            print ("  - False Negative: {}".format(self.false_negative["attack"][aname]))
            if self.attack_start_time:
                print ("  - Attack Start Time: {}".format(self.attack_start_time))
                print ("  - First Detection Time: {}".format(self.first_detection_time["attack"][aname]))
            print ("")

        idx = 0
        print ("2. Infection")
        for iname in self.inames:
            idx += 1
            print ("{}) {}".format(idx, iname))
            print ("  - Accuracy: {}".format(self.accuracy["infection"][iname]))
            print ("  - Precision: {}".format(self.precision["infection"][iname]))
            print ("  - Recall: {}".format(self.recall["infection"][iname]))
            print ("  - F1: {}".format(self.f1["infection"][iname]))
            print ("  - ROC AUC: {}".format(self.auc["infection"][iname]))
            print ("  - # of Training Samples: {}".format(len(self.training_set.get_dataset())))
            print ("  - # of Training Infection Samples: {}".format(self.training_set.get_num_of_types("infection")))
            print ("  - # of Training Packets: {}".format(self.training_packets))
            print ("  - # of Test Samples: {}".format(len(self.test_labels["infection"])))
            print ("  - # of Test Packets: {}".format(self.test_packets))
            print ("    # of benign windows: {}".format(self.num_of_benign_windows))
            print ("    # of infection windows: {}".format(self.num_of_infection_windows))
            print ("  - True Positive: {}".format(self.true_positive["infection"][iname]))
            print ("  - True Negative: {}".format(self.true_negative["infection"][iname]))
            print ("  - False Positive: {}".format(self.false_positive["infection"][iname]))
            print ("  - False Negative: {}".format(self.false_negative["infection"][iname]))
            if self.infection_start_time:
                print ("  - infection Start Time: {}".format(self.infection_start_time))
                print ("  - First Detection Time: {}".format(self.first_detection_time["infection"][iname]))
            print ("")

        idx = 0
        print ("3. Reconnaissance")
        for rname in self.rnames:
            idx += 1
            print ("{}) {}".format(idx, rname))
            print ("  - Accuracy: {}".format(self.accuracy["reconnaissance"][rname]))
            print ("  - Precision: {}".format(self.precision["reconnaissance"][rname]))
            print ("  - Recall: {}".format(self.recall["reconnaissance"][rname]))
            print ("  - F1: {}".format(self.f1["reconnaissance"][rname]))
            print ("  - ROC AUC: {}".format(self.auc["reconnaissance"][rname]))
            print ("  - # of Training Samples: {}".format(len(self.training_set.get_dataset())))
            print ("  - # of Training Reconnaissance Samples: {}".format(self.training_set.get_num_of_types("reconnaissance")))
            print ("  - # of Training Packets: {}".format(self.training_packets))
            print ("  - # of Test Samples: {}".format(len(self.test_labels["reconnaissance"])))
            print ("  - # of Test Packets: {}".format(self.test_packets))
            print ("    # of benign windows: {}".format(self.num_of_benign_windows))
            print ("    # of reconnaissance windows: {}".format(self.num_of_reconnaissance_windows))
            print ("  - True Positive: {}".format(self.true_positive["reconnaissance"][rname]))
            print ("  - True Negative: {}".format(self.true_negative["reconnaissance"][rname]))
            print ("  - False Positive: {}".format(self.false_positive["reconnaissance"][rname]))
            print ("  - False Negative: {}".format(self.false_negative["reconnaissance"][rname]))
            if self.reconnaissance_start_time:
                print ("  - reconnaissance Start Time: {}".format(self.reconnaissance_start_time))
                print ("  - First Detection Time: {}".format(self.first_detection_time["reconnaissance"][rname]))
            print ("")

        if self.core.is_self_evolving():
            idx = 0
            print ("4. Infection (After)")
            for iname in self.inames:
                idx += 1
                print ("{}) {}".format(idx, iname))
                print ("  - Accuracy: {}".format(self.accuracy["evolution"][iname]))
                print ("  - Precision: {}".format(self.precision["evolution"][iname]))
                print ("  - Recall: {}".format(self.recall["evolution"][iname]))
                print ("  - F1: {}".format(self.f1["evolution"][iname]))
                print ("  - ROC AUC: {}".format(self.auc["evolution"][iname]))
                print ("  - # of Test Samples: {}".format(len(self.test_labels["evolution"])))
                print ("  - # of Test Packets: {}".format(self.retest_packets))
                print ("    # of benign windows: {}".format(self.num_of_ebenign_windows))
                print ("    # of infection windows: {}".format(self.num_of_einfection_windows))
                print ("  - True Positive: {}".format(self.true_positive["evolution"][iname]))
                print ("  - True Negative: {}".format(self.true_negative["evolution"][iname]))
                print ("  - False Positive: {}".format(self.false_positive["evolution"][iname]))
                print ("  - False Negative: {}".format(self.false_negative["evolution"][iname]))
                print ("")

async def model(mm):
    logging.info("Run Model Manager")

    while True:
        usleep(THREAD_USLEEP_TIME)
        if not mm.is_model_generated:
            try:
                window = mm.queue.pop(0)
#                print("Model Manager> {}) {}: Window Start Time: {} / Window End Time: {} / Packets in Window (Forward): {} / Packets in Window (Backward): {}".format(window.get_serial_number(), window.get_flow_info("forward"), window.get_window_start_time(), window.get_window_end_time(), window.get_num_of_packets("forward"), window.get_num_of_packets("backward")))
            except:
                window = None
            await mm.learning(window)
        elif mm.core.get_is_testing():
            try:
                window = mm.queue.pop(0)
            except:
                window = None
            await mm.detection(window)
        elif mm.core.get_is_retesting():
            try:
                window = mm.queue.pop(0)
            except:
                window = None
            await mm.redetection(window)

    logging.info("Quit Model Manager")

def run(mm, loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(model(mm))

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--encoder", required=True, help="Encoder to be used", type=str)
    parser.add_argument("-l", "--log", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str)

    args = parser.parse_args()
    return args

def main():
    args = command_line_args()

    logging.basicConfig(level=args.log)
    encoding_manager = EncodingManager(args.conf)

if __name__ == "__main__":
    main()
