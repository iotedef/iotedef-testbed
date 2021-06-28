import argparse
import time
import logging
import threading
import sys
sys.path.append("..")
from utils.futils import init_features

usleep = lambda x: time.sleep(x/1000000.0)
THREAD_USLEEP_TIME=100000
PROCESS_TIMEOUT=3/1000000.0

class FeatureExtractor:
    def __init__(self, core, enabled):
        self.core = core
        self.features = []
        self.config = enabled
        init_features(self)

        self.cnt = 1
        self.queue = []
        self.queue_lock = threading.Lock()
        fe = threading.Thread(target=self.run, daemon=True)
        fe.start()

    def add_window(self, window):
        with self.queue_lock:
            window.set_serial_number(self.cnt)
#            print("Feature Extractor 1> {}) {}: Window Start Time: {} / Window End Time: {} / Packets in Window (Forward): {} / Packets in Window (Backward): {}".format(window.get_serial_number(), window.get_flow_info("forward"), window.get_window_start_time(), window.get_window_end_time(), window.get_num_of_packets("forward"), window.get_num_of_packets("backward")))
            self.queue.append(window)
            self.cnt += 1

    def add_feature(self, feature):
        if self.config[feature.get_name()]:
            self.features.append(feature)
            logging.debug("Feature {} is loaded".format(feature.get_name()))

    def get_queue_length(self):
        return len(self.queue)

    def run(self):
        logging.info("Run Feature Extractor")

        while len(self.queue) == 0:
            pass

        while True:
            usleep(THREAD_USLEEP_TIME)
            self.process_windows()
        logging.info("Quit Feature Extractor")

    def process_windows(self):
        while True:
            if len(self.queue) == 0:
                break

            window = self.queue.pop(0)
            #print ("Feature Extractor 2> {}) {}: Window Start Time: {} / Window End Time: {} / Packets in Window (Forward): {} / Packets in Window (Backward): {}".format(window.get_serial_number(), window.get_flow_info("forward"), window.get_window_start_time(), window.get_window_end_time(), window.get_num_of_packets("forward"), window.get_num_of_packets("backward")))
            #print ("Feature Extractor 2> {}) {}".format(window.get_serial_number(), window))

            self.extract_feature(window)

    def extract_feature(self, window):
        logging.debug("extract_feature()")
        for f in self.features:
            f.extract_feature(window)
        logging.debug("Window's label in FeatureExtractor (Attack Label: {}, Infection Label: {}, Reconnaissance Label: {})".format(window.get_label("attack"), window.get_label("infection"), window.get_label("reconnaissance")))
        self.core.send_window_to_encoding_manager(window)

    def parse_config(self, cname):
        ret = {}
        with open(cname, "r") as f:
            for line in f:
                if line.strip().startswith("#"):
                    continue
                if line.strip() == "":
                    continue

                name, tf = line.strip().split(",")
                name = name.strip()
                tf = tf.strip()

                if tf == "True":
                    val = True
                else:
                    val = False

                ret[name] = val
        return ret

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--features", required=True, help="Features considered", type=str)
    parser.add_argument("-l", "--log", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")

    args = parser.parse_args()
    return args

def main():
    args = command_line_args()

    logging.basicConfig(level=args.log)
    feature_extractor = FeatureExtractor(None, args.features)

if __name__ == "__main__":
    main()
