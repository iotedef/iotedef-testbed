class Feature:
    def __init__(self, name, ftype):
        self.name = name
        self.ftype = ftype      # Feature type (packet/flow)

    def get_name(self):
        return self.name

    def get_type(self):
        return self.ftype

    def extract_feature(self, window):
        pass
