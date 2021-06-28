import argparse
import time
import threading
import logging
import sys
import copy
sys.path.append("..")
from definitions.window import Window
from definitions.packet import Packet
from utils.network import extract_flow_info

usleep = lambda x: time.sleep(x/1000000.0)
WAITING_USLEEP_TIME=10000
SLIDING_WINDOW_TIME=10000

class WindowManager:
    def __init__(self, core, period, swnd):
        self.core = core
        self.period = period
        self.sliding_window = swnd
        self.windows = []
        self.queue = []
        self.queue_lock = threading.Lock()
        self.last_timestamp = time.time()

        wm = threading.Thread(target=self.run, daemon=True)
        wm.start()

    def get_queue_length(self):
        return len(self.queue)

    def get_period(self):
        return self.period

    def add_packet(self, pkt):
        self.queue.append(pkt)
    
    def run(self):
        if self.sliding_window:
            logging.info("Run Window Manager with Sliding Window")
        else:
            logging.info("Run Window Manager without Sliding Window")

        while len(self.queue) == 0:
            usleep(WAITING_USLEEP_TIME)
            pass

        while True:
            if self.sliding_window:
                usleep(SLIDING_WINDOW_TIME)
            else:
                time.sleep(self.period)
            self.process_packets()
            self.process_windows()
        logging.info("Quit Window Manager")

    def process_packets(self):
        stime = time.time()

        while True:
            if len(self.queue) == 0:
                break

            pkt = self.queue.pop(0)

            try:
                protocol, saddr, sport, daddr, dport = pkt.get_each_flow_info()
                wnd = Window(protocol, saddr, sport, daddr, dport, self.period)
                found = False
                for window in self.windows:
                    if window.is_corresponding_flow(wnd):
                        found = True
                        window.add_packet(pkt)
                        del wnd
                        break

                if not found:
                    wnd.add_packet(pkt)
                    self.windows.append(wnd)

            except:
                continue

    def process_windows(self):
        #logging.debug("invoke process_windows()")
        stime = time.time()
        self.last_timestamp = stime

        if len(self.windows) == 0:
            wnd = Window(0, 0, 0, 0, 0, self.period, dummy=True)
            if (self.core.get_tcpreplay_start_for_training and not self.core.get_tcpreplay_end_for_training) or (self.core.get_tcpreplay_start_for_testing and not self.core.get_tcpreplay_end_for_testing):
                self.core.send_window_to_feature_extractor(wnd)
        else:
            ts = self.last_timestamp - self.period
            if self.sliding_window:
                for window in self.windows:

                    fpkts = window.get_packets("forward")
                    fpkts = sorted(fpkts, key=lambda x: x.get_timestamp())
                    found = False
                    for i in range(len(fpkts)):
                        if fpkts[i].get_timestamp() > ts:
                            found = True
                            break
                    if found:
                        logging.debug("{} packets are dropped out of {}".format(i+1, len(fpkts)))
                        window.set_packets("forward", fpkts[i+1:])
                    else:
                        window.set_packets("forward", [])

                    bpkts = window.get_packets("backward")
                    bpkts = sorted(bpkts, key=lambda x: x.get_timestamp())
                    found = False
                    for i in range(len(bpkts)):
                        if bpkts[i].get_timestamp() > ts:
                            found = True
                            break
                    if found:
                        logging.debug("{} packets are dropped out of {}".format(i+1, len(bpkts)))
                        window.set_packets("backward", bpkts[i+1:])
                    else:
                        window.set_packets("backward", [])

                    logging.debug("window_manager> Window's label in WindowManager (Attack Label: {}, Infection Label: {}, Reconnaissance: {})".format(window.get_label("attack"), window.get_label("infection"), window.get_label("reconnaissance")))
            
                    if window.get_num_of_packets("both") == 0:
                        self.windows.remove(window)
                    else:
                        window.set_times(ts, self.last_timestamp)
                        self.core.send_window_to_feature_extractor(copy.deepcopy(window))
            else:
                while True:
                    if len(self.windows) == 0:
                        break
                    window = self.windows.pop(0)
                    window.set_times(ts, self.last_timestamp)
                    self.core.send_window_to_feature_extractor(window)
