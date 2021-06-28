import argparse
import time
import logging
import threading
import sys
sys.path.append("..")
from utils.eutils import init_encoders

usleep = lambda x: time.sleep(x/1000000.0)
THREAD_USLEEP_TIME=1000
PROCESS_TIMEOUT=3/1000000.0

class EncodingManager:
    def __init__(self, core, ename):
        self.core = core
        self.ename = ename
        self.encoders = {}
        init_encoders(self)
        if ename not in self.encoders:
            logging.error("Initializing EncodingManager error: No encoder exist: {}".format(ename))
            sys.exit(1)

    def add_window(self, window):
        self.encoding(window)

    def add_encoder(self, encoder):
        self.encoders[encoder.get_name()] = encoder
        logging.debug("Encoder {} is loaded".format(encoder.get_name()))

    def encoding(self, window):
        logging.debug("encoding with {}".format(self.ename))
        self.encoders[self.ename].encoding(window)
        logging.debug("Window's label in EncodingManager (Attack Label: {}, Infection Label: {}, Reconnaissance Label: {})".format(window.get_label("attack"), window.get_label("infection"), window.get_label("reconnaissance")))

#        print ("Encoding Manager> {}) {}: Window Start Time: {} / Window End Time: {} / Packets in Window (Forward): {} / Packets in Window (Backward): {}".format(window.get_serial_number(), window.get_flow_info("forward"), window.get_window_start_time(), window.get_window_end_time(), window.get_num_of_packets("forward"), window.get_num_of_packets("backward")))
        self.core.send_window_to_model_manager(window)

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
