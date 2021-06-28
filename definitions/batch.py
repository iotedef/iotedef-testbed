class Batch():
    def __init__(self, sequence, start, width, granularity):
        self.sequence = sequence
        self.width = width
        self.start_time = start
        self.end_time = start + width * granularity

    def get_sequence(self):
        return self.sequence

    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time

    def get_width(self):
        return self.width
