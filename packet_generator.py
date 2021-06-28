import argparse
import time
import logging
import socket
import os
import sys
import asyncio
import threading
import subprocess

usleep = lambda x: time.sleep(x/1000000.0)
BUF_SIZE = 256
CHECK_USLEEP_TIME=10000

class PacketGenerator:
    def __init__(self, port, home, interface):
        self.home = home
        self.interface = interface
        self.sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", port))

        loop = asyncio.new_event_loop()
        pg = threading.Thread(target=run, args=(self, loop,))
        pg.start()

async def main_loop(pg):
    sock = pg.sock
    while True:
        msg, clnt = sock.recvfrom(BUF_SIZE)
        op, device, dataset, timestamp = msg.decode().split(":")
        device = int(device)
        dataset = int(dataset)
        timestamp = int(timestamp)
        logging.debug("op: {}, device: {}, dataset: {}, timestamp: {}, clnt: {}".format(op, device, dataset, timestamp, clnt))

        if check_availability(pg.home, op, device, dataset):
            sock.sendto("{}:available".format(op).encode(), clnt)
        else:
            sock.sendto("{}:unavailable".format(op).encode(), clnt)
        await process_operation(pg, clnt, op, device, dataset, timestamp)

async def process_operation(pg, clnt, op, device, dataset, timestamp):
    logging.debug("op: {}, device number: {}, dataset number: {}, start time: {}".format(op, device, dataset, timestamp))

    pcap_file = "{}/set_{}/{}_{}.pcap".format(pg.home, dataset, op, device)
    cmd = ["tcpreplay", "-i", pg.interface, pcap_file]
    logging.info("Tcpreplay command: {}".format(cmd))
    curr = int(time.time())
    logging.debug("current timestamp: {}".format(curr))

    while curr < timestamp:
        curr = int(time.time())
        usleep(CHECK_USLEEP_TIME)

    logging.debug("current timestamp: {}".format(int(time.time())))
    subprocess.call(cmd)
    logging.info("Tcpreplay finished for {}".format(pcap_file))
    pg.sock.sendto("{}:done".format(op).encode(), clnt)

def check_availability(home, op, device, dataset):
    pcap_file = "{}/set_{}/{}_{}.pcap".format(home, dataset, op, device)
    logging.debug("Check availability of the file {}".format(pcap_file))

    if os.path.exists(pcap_file):
        ret = True
    else:
        ret = False

    return ret

def run(pg, loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_loop(pg))

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", metavar="<port number to listen>", help="Port Number to Listen", type=int, default=20001)
    parser.add_argument("-d", "--dataset", metavar="<home directory of the datasets>", help="Home directory of the datasets", type=str, required=True)
    parser.add_argument("-i", "--interface", metavar="<interface to be used>", help="Interface to be used", type=str, required=True)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)

    home = os.path.abspath(args.dataset)
    if not os.path.exists(home):
        logging.error("Error in the home directory of dataset: {}".format(home))
        sys.exit(1)

    logging.debug("Home directory: {}".format(home))

    packet_generator = PacketGenerator(args.port, home, args.interface)

if __name__ == "__main__":
    main()
