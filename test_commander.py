import argparse
import socket
import logging
import time

def exchange_test_message(addr, port):
    sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    msg = "training:0:13:{}".format(int(time.time()+5)).encode()
    sock.sendto(msg, (addr, port))
    msg, srvr = sock.recvfrom(256)
    msg = msg.decode()
    logging.info("msg: {} from {}".format(msg, srvr))
    msg, srvr = sock.recvfrom(256)
    msg = msg.decode()
    logging.info("msg: {} from {}".format(msg, srvr))

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", metavar="<IP address to connect>", help="IP address to connect", required=True, type=str)
    parser.add_argument("-p", "--port", metavar="<port number to connect>", help="Port number to connect", required=True, type=int)
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logging.basicConfig(level=args.log)
    
    exchange_test_message(args.address, args.port)

if __name__ == "__main__":
    main()
