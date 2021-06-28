import socket
import os
import argparse
import logging
import dpkt
import threading
import sys
import time
import pcapy
import asyncio
import socket
import ctypes
import copy
sys.path.append("..")
from definitions.packet import Packet
from utils.network import extract_flow_info
from ctypes.util import find_library

usleep = lambda x: time.sleep(x/1000000.0)
THREAD_USLEEP_TIME=0.1
BUF_SIZE = 16384
OFFSET = 0.2
PCAP_ERRBUF_SIZE = 256

class timeval(ctypes.Structure):
    _fields_ = [('tv_sec', ctypes.c_long),
            ('tv_usec', ctypes.c_long)]

class pcap_pkthdr(ctypes.Structure):
    _fields_ = [("ts", timeval), 
            ("caplen", ctypes.c_uint), 
            ("len", ctypes.c_uint)]

libpcap = ctypes.cdll.LoadLibrary(find_library("pcap"))

pcap_open_live = libpcap.pcap_open_live
pcap_open_live.restype = ctypes.POINTER(ctypes.c_void_p)

pcap_can_set_rfmon = libpcap.pcap_can_set_rfmon
pcap_can_set_rfmon.argtypes = [ctypes.c_void_p]

pcap_next = libpcap.pcap_next
pcap_next.restype = ctypes.POINTER(ctypes.c_char)
pcap_next.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(pcap_pkthdr)]

pcap_next_ex = libpcap.pcap_next_ex
pcap_next_ex.restype = ctypes.c_int

dev = bytes(str('lo'), 'ascii')
snaplen = ctypes.c_int(2048)
promisc = ctypes.c_int(1)
to_ms = ctypes.c_int(0)
errbuf = ctypes.create_string_buffer(PCAP_ERRBUF_SIZE)

class PacketCapturer:
    def __init__(self, core, training_label=None, test_label=None):
        self.core = core
        self.training_label = training_label
        self.test_label = test_label
        self.labels = 0
        self.handle = pcap_open_live(dev, snaplen, promisc, to_ms, errbuf)
        self.training_start_time = None
        self.test_start_time = None 
        self.running = True
        self.num = 0
        self.cnt = 1
        self.queue = []

        loop = asyncio.new_event_loop()
        pl = threading.Thread(target=run, args=(self, loop, ), daemon=True)
        #pl = threading.Thread(target=run, args=(self, loop, ))
        pl.start()

    def quit(self):
        self.running = False

    def get_queue_length(self):
        return len(self.queue)

    def get_cnt(self):
        return self.cnt

#async def pp(pcap):
async def pp(pcap, num, header, packet):
    ts = time.time()
#    num, header, packet = pcap.queue.pop(0)
#    logging.info("Packet Number: {}".format(num))

    pkt = parse_packet(ts, header, packet)
    if pkt:
        if pcap.core:
            if pcap.core.get_tcpreplay_start_for_training() and not pcap.core.get_tcpreplay_end_for_training():
                if not pcap.core.get_training_start_time():
                    pcap.cnt = 0
                    pcap.core.set_training_start_time(ts)
                    pcap.training_start_time = ts
                #pcap.cnt = await check_label(pkt, pcap.cnt, pcap.training_label)
                pcap.cnt += 1
                if pcap.cnt % 1000 == 0:
                    logging.info("cnt: {}, key: {}, label: {}, queue: {}".format(pcap.cnt, pkt.get_flow_info(), pkt.get_label(), len(pcap.queue)))
            elif pcap.core.get_tcpreplay_start_for_testing() and not pcap.core.get_tcpreplay_end_for_testing():
                if not pcap.core.get_test_start_time():
                    pcap.num = 1
                    pcap.cnt = 0
                    pcap.core.set_test_start_time(ts)
                    pcap.test_start_time = ts
                #pcap.cnt = await check_label(pkt, pcap.cnt, pcap.test_label)
                pcap.cnt += 1
                if pcap.cnt % 1000 == 0:
                    logging.info("cnt: {}, key: {}, label: {}, queue: {}".format(pcap.cnt, pkt.get_flow_info(), pkt.get_label(), len(pcap.queue)))

            elif pcap.core.get_tcpreplay_start_for_retesting() and not pcap.core.get_tcpreplay_end_for_retesting():
                if not pcap.core.get_retest_start_time():
                    pcap.num = 1
                    pcap.cnt = 0
                    pcap.core.set_retest_start_time(ts)
                    pcap.retest_start_time = ts
                #pcap.cnt = await check_label(pkt, pcap.cnt, pcap.test_label)
                pcap.cnt += 1
                if pcap.cnt % 1000 == 0:
                    logging.info("cnt: {}, key: {}, label: {}, queue: {}".format(pcap.cnt, pkt.get_flow_info(), pkt.get_label(), len(pcap.queue)))

            if pcap.core.get_tcpreplay_start_for_testing() and pcap.core.get_attack_start_time() == None and pkt.get_label() == 1:
                logging.debug(">>> Attack Start Time: {}".format(ts))
                pcap.core.set_attack_start_time(ts)
        else:
            pcap.cnt += 1
            #pcap.cnt = await check_label(pkt, pcap.cnt, pcap.training_label)
            if pkt.get_label() == 2:
                logging.debug("cnt: {}, key: {}, label: {}, queue: {}".format(pcap.cnt-1, pkt.get_flow_info(), pkt.get_label(), len(pcap.queue)))

        if pcap.core and pkt.get_label() != -1:
            pcap.core.send_packet_to_window_manager(pkt)
    else:
        pcap.cnt += 1

async def capturer(pcap):
    logging.info("Run Packet Capturer")
    num = 0
    hbuf = pcap_pkthdr()

    while pcap.running:
        pbuf = pcap_next(pcap.handle, ctypes.byref(hbuf))
        pcap.num += 1
        header = pcap_pkthdr()
        header.len = hbuf.len
        header.caplen = hbuf.caplen
        header.ts.tv_sec = hbuf.ts.tv_sec
        header.ts.tv_usec = hbuf.ts.tv_usec
        packet = pbuf[:header.len]
        logging.debug("Packet capturered: {} ({} bytes)".format(pcap.num, header.len))
#        pcap.queue.append((num, header, packet))
        await pp(pcap, pcap.num, header, packet)
    logging.info("Quit Packet Capturer")

def run(pcap, loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(capturer(pcap))

def mac_addr(addr):
    return "{:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}".format(addr[0], addr[1], addr[2], addr[3], addr[4], addr[5])

def inet_to_str(addr):
    try:
        return socket.inet_ntop(socket.AF_INET, addr)
    except:
        return socket.inet_ntop(socket.AF_INET6, addr)

def parse_packet(ts, header, packet):
    eth = dpkt.ethernet.Ethernet(packet)

    if not isinstance(eth.data, dpkt.ip.IP):
        logging.debug("Non IP Packet type not supported {}".format(eth.data.__class__.__name__))
        return None

    length = len(packet)
    ip = eth.data
    df = bool(ip.off & dpkt.ip.IP_DF)
    mf = bool(ip.off & dpkt.ip.IP_MF)
    offset = bool(ip.off & dpkt.ip.IP_OFFMASK)

    protocol = ip.p
    trans = None

    if protocol == 1:
        logging.debug("ICMP: {} -> {}".format(inet_to_str(ip.src), inet_to_str(ip.dst)))

    elif protocol == 6:
        if not isinstance(ip.data, dpkt.tcp.TCP):
            #logging.error("TCP Parsing Error")
            return None
        tcp = ip.data
        sport = tcp.sport
        dport = tcp.dport
        logging.debug("TCP/IP: {}:{} -> {}:{} (len={})".format(inet_to_str(ip.src), sport, inet_to_str(ip.dst), dport, ip.len))
        trans = tcp
        key = "{}:{}:{}:{}".format(inet_to_str(ip.src), sport, inet_to_str(ip.dst), dport)

    elif protocol == 17:
        if not isinstance(ip.data, dpkt.udp.UDP):
            #logging.error("UDP Parsing Error")
            return None
        udp = ip.data
        sport = udp.sport
        dport = udp.dport
        logging.debug("UDP/IP: {}:{} -> {}:{} (len={})".format(inet_to_str(ip.src), sport, inet_to_str(ip.dst), dport, ip.len))
        trans = udp
        key = "{}:{}:{}:{}".format(inet_to_str(ip.src), sport, inet_to_str(ip.dst), dport)

    else:
        logging.error("Not supported protocol")
        return None

    return Packet(ts, header, eth, ip, trans, length)

async def check_label(pkt, cnt, labels):
    key = pkt.get_flow_info()
    none = labels["none"]
    tpkts = max(none)

    while cnt in none and none[cnt]:
        cnt += 1

    if cnt <= tpkts and key in labels:
        try:
            pkt.set_label(labels[key][cnt])
            cnt += 1
        except:
            #logging.error("error: {}".format(cnt))
            if key in labels:
                found = False
                while True:
                    if cnt not in labels[key]:
                        cnt += 1
                        if cnt > max(labels[key]):
                            break
                    else:
                        found = True
                        break
                if found:
                    pkt.set_label(labels[key][cnt])
                else:
                    pkt.set_label(-1)
            else:
                pkt.set_label(-1)
            logging.debug("cnt: {}, key: {}, label: {}".format(cnt, key, pkt.get_label()))
            cnt += 1

    return cnt

def parse_label(fname):
    ret = {}
    ret["none"] = {}

    with open(fname, "r") as f:
        cnt = 1
        for line in f:
            tmp = line.strip().split(", ")
            num = int(tmp[0])
            while cnt < num:
                ret["none"][cnt] = 1
                cnt += 1
            ret["none"][cnt] = 0
            key = "{}:{}-{}:{}".format(tmp[3], int(tmp[4]), tmp[5], int(tmp[6]))
            if key not in ret:
                ret[key] = {}
            ret[key][cnt] = int(tmp[-1])
            cnt += 1
    ret["none"][cnt] = 0
    return ret

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", metavar="<dataset index>", help="dataset index", type=int, required=True)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str)
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logLevel = args.log
    logging.basicConfig(level=logLevel)
    sidx = args.d
    #tlname = "../../dataset/set_{}/training.label".format(sidx)
    #elname = "../../dataset/set_{}/test.label".format(sidx)
    #tl = parse_label(tlname)
    #el = parse_label(elname)

    #plistener = PacketCapturer(None, tl, el)
    plistener = PacketCapturer(None)

if __name__ == "__main__":
    main()
