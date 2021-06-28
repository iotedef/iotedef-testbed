class Flow:
    def __init__(self, protocol, saddr, sport, daddr, dport):
        self.protocol = protocol
        self.saddr = saddr
        self.sport = sport
        self.daddr = daddr
        self.dport = dport
        self.stat = {} # map: feature -> value

    def is_corresponding_flow(self, flow):
        return self.protocol == flow.get_protocol() and self.saddr == flow.get_saddr() and self.sport == flow.get_sport() and self.daddr == flow.get_daddr() and self.dport == flow.get_dport()

    def get_protocol(self):
        return self.protocol

    def get_saddr(self):
        return self.saddr

    def get_sport(self):
        return self.sport

    def get_daddr(self):
        return self.daddr

    def get_dport(self):
        return self.dport

    def add_feature_value(self, feature, val):
        self.stat[feature] = self.stat[feature] + val

    def get_feature_value(self, feature):
        return self.stat[feature]
