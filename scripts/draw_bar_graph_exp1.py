import argparse
import logging
from matplotlib import pyplot as plt

def create_x(t, w, n, d):
    return [t*x + w*n for x in range(d)]

def draw_graph():
    topics = ["0 (4)", "1 (286)", "2 (1.77e+5)", "5 (1.67e+14)", "10 (1.67e+26)", "15 (1.67e+41)"]

    plt.rcParams["font.family"] = "Times New Roman"
    plt.rcParams["font.size"] = 16
    plt.figure(figsize=(10, 4), dpi=100).tight_layout()

    baseline = [0.5, 0.39, 0.35, 0.43, 0.41, 0.35]
    f1 = [0.76, 0.94, 0.74, 0.74, 0.72, 0.65]

    increment = []
    for i in range(len(baseline)):
        increment.append(f1[i] - baseline[i])

    baseline_x = create_x(3, 0.8, 1, 6)
    f1_x = create_x(3, 0.8, 2, 6)
    increment_x = create_x(3, 0.8, 3, 6)

    ax = plt.subplot()
    b = ax.bar(baseline_x, baseline, color="white", edgecolor="black")
    f = ax.bar(f1_x, f1, color="black")
    i = ax.bar(increment_x, increment, color="white", hatch="/", edgecolor="black")

    middle_x = [(a+b+c)/3 for (a,b,c) in zip(baseline_x, f1_x, increment_x)]
    ax.set_xticks(middle_x)
    ax.set_xticklabels(topics)
    plt.legend([b, f, i], ["baseline", "attention", "increment"], loc="lower center", bbox_to_anchor=(0.5, -0.45), ncol=3)
    
#    plt.xticks()
    plt.xlabel("d (# of words)")
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
