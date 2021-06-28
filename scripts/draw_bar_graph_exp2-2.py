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

    precision_wo = [0.18, 0.85, 0.64, 0.19, 0.25]
    precision_w = [0.26, 0.87, 0.55, 0.45, 0.81]
    recall_wo = [1.0, 0.74, 0.85, 1.0, 1.0]
    recall_w = [0.82, 0.74, 0.84, 0.99, 0.96]

    precision_wo_x = create_x(4, 0.8, 1, 5)
    precision_w_x = create_x(4, 0.8, 2, 5)
    recall_wo_x = create_x(4, 0.8, 3, 5)
    recall_w_x = create_x(4, 0.8, 4, 5)

    ax = plt.subplot()
    p_wo = ax.bar(precision_wo_x, precision_wo, color="white", edgecolor="black")
    p_w = ax.bar(precision_w_x, precision_w, color="black")
    r_wo = ax.bar(recall_wo_x, recall_wo, color="white", hatch="/", edgecolor="black")
    r_w = ax.bar(recall_w_x, recall_w, color="gray")

    middle_x = [(a+b+c+d)/4 for (a,b,c,d) in zip(precision_wo_x, precision_w_x, recall_wo_x, recall_w_x)]
    ax.set_xticks(middle_x)
    ax.set_xticklabels(topics)
    
    plt.legend((p_wo, p_w, r_wo, r_w), ("Precision w/o Attention", "Precision w/ Attention", "Recall w/o Attention", "Recall w/ Attention"), loc="lower center", bbox_to_anchor=(0.5, -0.47), ncol=2)
    plt.xlabel("Classifiers")
    plt.ylabel("Value")
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
