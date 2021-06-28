import argparse
import logging
from matplotlib import pyplot as plt

def create_x(t, w, n, d):
    return [t*x + w*n for x in range(d)]

def draw_graph():
    topics = ['baseline', 'strategy 1', 'strategy 2', 'strategy 3']
    keys = ["base", "st1", "st2", "st3"]

    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 14
    plt.figure(figsize=(10, 4), dpi=100).tight_layout()

    precision = [0.19, 0.77, 0.82, 0.64]
    recall = [1.0, 0.98, 0.94, 0.88]
    f1 = [0.31, 0.82, 0.87, 0.72]

    precision_x = create_x(3, 0.8, 1, 4)
    recall_x = create_x(3, 0.8, 2, 4)
    f1_x = create_x(3, 0.8, 3, 4)

    ax = plt.subplot()
    p = ax.bar(precision_x, precision, color="black")
    r = ax.bar(recall_x, recall, color="white", edgecolor="black")
    f = ax.bar(f1_x, f1, color="white", hatch="/", edgecolor="black")

    middle_x = [(a+b+c)/3 for (a,b,c) in zip(precision_x, recall_x, f1_x)]
    ax.set_xticks(middle_x)
    ax.set_xticklabels(topics)
    plt.legend((p, r, f), ("Precision", "Recall", "F1 Score"), loc="lower center", bbox_to_anchor=(0.5, -0.45), ncol=3)

    plt.xlabel("Strategies")
    plt.ylabel("Values")
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
