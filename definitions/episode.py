from definitions.window import Window
import logging

class Episode:
    def __init__(self, aname, serial, window, nodes, maps=None):
        self.algo = aname
        self.nodes = nodes
        self.serial = serial
        self.automata = {}
        self.partial_order = True
        self.freq_count = 0
        self.in_window = 0
        self.block_start = 0
        self.windows = []
        self.maps = maps
        self.add_window(window)

    def is_corresponding_flow(self, window):
        if len(self.windows) > 0:
            return self.windows[0].is_corresponding_flow(window)
        else:
            return False

    def add_window(self, window):
        self.windows.append(window)

    def get_windows(self): # get_nodes()
        return self.windows

    def get_num_of_windows(self): # get_size()
        return len(self.windows)
    
    def get_algo_name(self):
        return self.algo

    def get_feature_names(self):
        ret = None
        if len(self.windows) > 0:
            ret = self.windows[0].get_feature_names()
        return ret
    
    def get_serial_number(self):
        return self.serial

    def set_block_start(self, block_start):
        self.block_start = block_start

    def get_block_start(self):
        return self.block_start

    def get_nodes(self):
        return self.nodes

    def get_size(self):
        return len(self.nodes)

    def set_initialized(self, n, val):
        self.automata[n] = val

    def get_initialized(self, n):
        return self.automata[n]

    def set_freq_count(self, count):
        self.freq_count = count

    def get_freq_count(self):
        return self.freq_count

    def set_in_window(self, time):
        self.in_window = time

    def get_in_window(self):
        return self.in_window

    def get_frequency(self, sequence):
        lst = sequence.get_sequence()
        batches = sequence.get_batches()

        cnt = 0
        for b in batches:
            cnt += self.occur(b)
        logging.info("Node: {}, Count: {}".format(self.nodes, cnt))

        return cnt

    def get_maps(self):
        return self.maps

    def get_code(self):
        ret = ""
        for e in self.nodes.values():
            ret += str(e)
        return ret

    def occur(self, batch):
        episode = self.nodes

        # TODO: The following events list should be revised; a window can have more than one label
        events = []
        for w in batch.get_sequence():
            idx = 0
            if w.get_label("attack") == 1:
                idx = 1
            elif w.get_label("reconnaissance") == 1:
                idx = 3
            elif w.get_label("infection") == 1:
                idx = 2
            events.append(self.maps[idx])
        ret = 1

        logging.debug("Episode: {}".format(episode))
        logging.debug("Events: {}".format(events))
        for n in episode:
            ev = episode[n]
            if ev not in events:
                ret = 0
                break
            else:
                idx = events.index(ev)
                events = events[idx+1:]
                logging.debug("idx: {} -> Events: {}".format(idx, events))

        return ret

    def compare(self, lst):
        ret = True
        for i in range(1, self.get_size() + 1):
            if self.nodes[i] != lst[i]:
                ret = False
        return ret
