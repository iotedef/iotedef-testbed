import numpy as np

class State():
    def __init__(self, serial, flow_info, fnames, values, label, labeled, probability, start_time, end_time, training):
        self.label = label
        self.labeled = labeled
        self.hidden_label = 0 
        # 'B': benign, 'A': attack, 'I': infection, 'R': reconnaissance
        self.probability = probability
        self.infection = 0
        self.stat = {}
        self.start_time = start_time
        self.end_time = end_time
        self.training = training
        self.flow_info = flow_info
        self.serial = serial

        for i in range(len(fnames)):
            self.stat[fnames[i]] = values[i]

    def get_flow_info(self):
        return self.flow_info

    def add_feature_value(self, feature, val):
        if feature not in self.stat:
            self.stat[feature] = 0
        self.stat[feature] = self.stat[feature] + val

    def get_feature_names(self):
        return list(self.stat.keys())

    def get_feature_value(self, feature):
        return self.stat[feature]

    def get_features(self):
        return list(self.stat.values())

    def get_serial_number(self):
        return self.serial

    def get_label(self, kind=None):
        if kind:
            return self.label[kind]
        else:
            return self.label

    def get_label_vector(self):
        if self.label["reconnaissance"] == 1:
            return [0, 1, 0, 0]
        elif self.label["infection"] == 1:
            return [0, 0, 1, 0]
        elif self.label["attack"] == 1:
            return [0, 0, 0, 1]
        else:
            return [1, 0, 0, 0]

    def get_labeled(self, kind=None):
        try:
            if kind:
                return self.labeled[kind]
            else:
                return self.labeled
        except:
            if kind:
                return 0
            else:
                return None

    def get_best_label(self):
        ret = 0
        val = 0

        if not self.training:
            for state in self.probability:
                if self.probability[state] > val:
                    val = self.probability[state]
                    if state == "attack":
                        ret = 1
                    elif state == "infection":
                        ret = 2
                    elif state == "reconnaissance":
                        ret = 3
                    else:
                        ret = 0
        else:
            if self.get_label("attack") == 1:
                ret = 1
            elif self.get_label("reconnaissance") == 1:
                ret = 3
            elif self.get_label("infection") == 1:
                ret = 2
            else:
                ret = 0

        return ret

    def get_best_label_string(self):
        idx = self.get_best_label()
        if idx == 0:
            ret = "benign"
        elif idx == 1:
            ret = "attack"
        elif idx == 2:
            ret = "infection"
        elif idx == 3:
            ret = "reconnaissance"
        return ret

    def get_best_label_char(self):
        idx = self.get_best_label()
        if idx == 0:
            ret = 'B'
        elif idx == 1:
            ret = 'A'
        elif idx == 2:
            ret = 'B'
        elif idx == 3:
            ret = 'R'
        return ret

    def set_label(self, label):
        self.label = label

    def get_hidden_label(self):
        return self.hidden_label

    def set_hidden_label(self, label):
        self.hidden_label = label

    def set_hidden_label_int(self, idx):
        if idx == 0:
            label = 'B'
        elif idx == 1:
            label = 'A'
        elif idx == 2:
            label = 'I'
        elif idx == 3:
            label = 'R'
        self.hidden_label = label

    def get_probability(self, kind=None):
        if kind:
            return self.probability[kind]
        else:
            return self.probability

    def get_probability_vector(self):
        return [self.probability["benign"], self.probability["reconnaissance"], self.probability["infection"], self.probability["attack"]]

    def get_probability_char(self, kind=None):
        if kind:
            if kind == "B":
                key = "benign"
            elif kind == "I":
                key = "infection"
            elif kind == "A":
                key = "attack"
            elif kind == "R":
                key = "reconnaissance"
            return self.probability[key]
        else:
            return self.probability

    def get_probability_int(self, kind=None):
        if kind >= 0 and kind < 4:
            if kind == 0:
                key = "benign"
            elif kind == 2:
                key = "infection"
            elif kind == 1:
                key = "attack"
            elif kind == 3:
                key = "reconnaissance"
            return self.probability[key]
        else:
            return self.probability

    def set_probability(self, probability):
        self.probability = probability

    def get_code(self):
        # code: [B, A, I, R]
        code = np.array([self.probability["benign"], self.probability["attack"], self.probability["infection"], self.probability["reconnaissance"]])
        return code

    def get_code_rounded(self, rv):
        if not self.training and rv > 0:
            code = np.array([round(self.probability["benign"], rv), round(self.probability["attack"], rv), round(self.probability["infection"], rv), round(self.probability["reconnaissance"], rv)])
        else:
            val = self.get_best_label()    
            if val == 0:
                code = [1.0, 0.0, 0.0, 0.0]
            elif val == 1:
                code = [0.0, 1.0, 0.0, 0.0]
            elif val == 2:
                code = [0.0, 0.0, 1.0, 0.0]
            elif val == 3:
                code = [0.0, 0.0, 0.0, 1.0]
        return code 

    def set_infection(self):
        self.infection = 1

    def get_infection(self):
        return self.infection

    def get_start_time(self):
        return self.start_time

    def get_end_time(self):
        return self.end_time
