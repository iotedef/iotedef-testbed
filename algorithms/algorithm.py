class Algorithm:
    def __init__(self, name):
        self.name = name
        self.classifier = {}
        self.scale = None

    def get_name(self):
        return self.name

    def learning(self, training_set, kind):
        pass

    def detection(self, window, kind):
        pass
