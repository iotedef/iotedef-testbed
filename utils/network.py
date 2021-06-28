import dpkt
import socket
import logging

def extract_flow_info(pkt):
    ip = dpkt.ip.IP(pkt)
    saddr = socket.inet_ntop(socket.AF_INET, ip.src)
    daddr = socket.inet_ntop(socket.AF_INET, ip.dst)
    protocol = ip.p
    sport = None
    dport = None
    
    if protocol == 1:
        logging.debug("ICMP ({}): Source IP: {}, Destination IP: {}".format(protocol, saddr, daddr))
    elif protocol == 6:
        tcp = ip.data
        sport = tcp.sport
        dport = tcp.dport
        logging.debug("TCP ({}): Source: {}:{}, Destination: {}:{}".format(protocol, saddr, sport, daddr, dport))
    elif protocol == 17:
        udp = ip.data
        sport = udp.sport
        dport = udp.dport
        logging.debug("UDP ({}): Source: {}:{}, Destination: {}:{}".format(protocol, saddr, sport, daddr, dport))
    else:
        logging.debug("Unknown ({}): Source IP: {}, Destination IP: {}".format(protocol, saddr, daddr))

    return protocol, saddr, sport, daddr, dport
