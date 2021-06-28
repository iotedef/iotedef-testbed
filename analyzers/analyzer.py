class Analyzer:
    def __init__(self, name):
        self.name = name
        self.model = None

    def get_name(self):
        return self.name

    def model_exists(self):
        ret = False
        if self.model:
            ret = True
        return ret

    def learning(self, sequence, config):
        pass

    def analysis(self, sequence, config):
        pass

    def print_infection_information(self, results, config):
        ofname = "{}/{}".format(config["home"], config["output"])
        print ("===== Infection Information =====")
        cnt = 0
        checked = []
        windows = []

        for prob, window in results:
            serial = window.get_serial_number()
            if serial not in checked:
                checked.append(serial)
                windows.append((prob, window))

        with open(ofname, "w") as of:
            of.write("Number, Confidence, Flow, Start Time, End Time, Answer Label, Classified Label, Classified Probability\n")
            for prob, infection in windows:
                cnt += 1

                print ("{}> Serial Number: {}".format(cnt, infection.get_serial_number()))
                print ("  - Confidence: {}".format(prob))
                print ("  - Flow: {}".format(infection.get_flow_info()))
                print ("  - Start Time: {}".format(infection.get_start_time()))
                print ("  - End Time: {}".format(infection.get_end_time()))
                print ("  - Answer Label: {}".format(infection.get_label("infection")))
                print ("  - Classified Label: {}".format(infection.get_labeled("infection")))
                print ("  - Classified Probability: {}".format(infection.get_probability("infection")))
                of.write("{}, {}, {}, {}, {}, {}, {}, {}\n".format(cnt, prob, infection.get_flow_info(), infection.get_start_time(), infection.get_end_time(), infection.get_label("infection"), infection.get_labeled("infection"), infection.get_probability("infection")))
