import socket
import dpkt
import logging

class Packet:
    def __init__(self, ts, header, eth, network, transport, length):
        self.timestamp = ts
        self.header = header
        self.eth = eth
        self.network = network
        self.transport = transport
        if self.transport:
            sport = self.transport.sport
            dport = self.transport.dport
            self.label = int(sport / 10000)
            if self.label > 3:
                self.label = 0
        else:
            self.label = 0
        self.length = length

    def get_timestamp(self):
        return self.timestamp

    def get_header(self):
        return self.header

    def get_ethernet(self):
        return self.eth

    def get_network_layer(self):
        return self.network

    def get_transport_layer(self):
        return self.transport

    def get_header_length(self):
        ret = 0
        ret += 14 # ethernet header length

        if isinstance(self.network, dpkt.ip.IP):
            ip = self.network
            ret += ip.hl

            if ip.p == socket.IPPROTO_TCP:
                tcp = self.transport
                ret += tcp.off
            elif ip.p == socket.IPPROTO_UDP:
                ret += 8
        
        return ret

    def is_fin(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if tcp.flags & dpkt.tcp.TH_FIN:
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def is_syn(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if (tcp.flags & dpkt.tcp.TH_SYN) and not (tcp.flags & dpkt.tcp.TH_ACK):
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def is_rst(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if tcp.flags & dpkt.tcp.TH_RST:
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def is_psh(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if tcp.flags & dpkt.tcp.TH_PUSH:
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def is_ack(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if tcp.flags & dpkt.tcp.TH_ACK:
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def is_urg(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if tcp.flags & dpkt.tcp.TH_URG:
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def is_cwr(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if tcp.flags & dpkt.tcp.TH_CWR:
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def is_ece(self):
        if not self.transport:
            ret = False
        else:
            if isinstance(self.transport, dpkt.tcp.TCP):
                tcp = self.transport
                if tcp.flags & dpkt.tcp.TH_ECE:
                    ret = True
                else:
                    ret = False
            else:
                ret = False
        return ret

    def get_flow_info(self):
        saddr = socket.inet_ntop(socket.AF_INET, self.network.src)
        daddr = socket.inet_ntop(socket.AF_INET, self.network.dst)
        if self.transport:
            sport = self.transport.sport % 10000
            dport = self.transport.dport % 10000
            ret = "{}:{}-{}:{}".format(saddr, sport, daddr, dport)
        else:
            ret = "{}-{}".format(saddr, daddr)
        return ret

    def get_each_flow_info(self):
        protocol = self.network.p
        saddr = socket.inet_ntop(socket.AF_INET, self.network.src)
        daddr = socket.inet_ntop(socket.AF_INET, self.network.dst)
        if self.transport:
            sport = self.transport.sport % 10000
            dport = self.transport.dport % 10000
        else:
            sport = None
            dport = None

        return protocol, saddr, sport, daddr, dport

    def set_label(self, label):
        self.label = label
        logging.debug("Packet is set to {}".format(self.label))

    def get_label(self):
        return self.label

    def get_packet_length(self):
        return self.length
        #return self.header.getcaplen()
