import argparse
import logging
from matplotlib import pyplot as plt

def create_x(t, w, n, d):
    return [t*x + w*n for x in range(d)]

def draw_graph():
    topics = ['Logistic Regression', 'Decision Tree', 'Random Forest', 'Feedforward', 'RNN with LSTM']
    keys = ["lr", "dt", "rf", "svm", "ff", "lstm"]

    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 14
    plt.figure(figsize=(10, 4), dpi=100).tight_layout()

    f1_wo = [0.31, 0.69, 0.66, 0.31, 0.39]
    f1_w = [0.39, 0.70, 0.59, 0.6, 0.87]

    f1_wo_x = create_x(2, 0.8, 1, 5)
    f1_w_x = create_x(2, 0.8, 2, 5)

    ax = plt.subplot()
    f1_wo = ax.bar(f1_wo_x, f1_wo, color="white", edgecolor="black")
    f1_w = ax.bar(f1_w_x, f1_w, color="black")

    middle_x = [(a+b)/2 for (a,b) in zip(f1_wo_x, f1_w_x)]
    ax.set_xticks(middle_x)
    ax.set_xticklabels(topics)
    
    plt.legend((f1_wo, f1_w), ("F1 Score w/o Attention", "F1 Score w/ Attention"), loc="lower center", bbox_to_anchor=(0.5, -0.47), ncol=2)
    plt.xlabel("Classifiers")
    plt.ylabel("F1 Score")
    plt.subplots_adjust(left=0.08, top=0.95, bottom=0.30, right=0.98)
    plt.show()

def command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log", metavar="<log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)>", help="Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)", type=str, default="INFO")
    args = parser.parse_args()
    return args

def main():
    args = command_line_args()
    logLevel = args.log
    logging.basicConfig(level=logLevel)
    
    draw_graph()

if __name__ == "__main__":
    main()
