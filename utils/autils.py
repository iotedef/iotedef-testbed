import sys
sys.path.append("..")
from algorithms.naive_bayes import NaiveBayes
from algorithms.svm import Svm
from algorithms.feedforward import Feedforward
from algorithms.logistic_regression import LogisticRegression
from algorithms.random_forest import RandomForest
from algorithms.decision_tree import DecisionTree
from algorithms.lstm import Lstm

def init_algorithms(model_manager):
    model_manager.add_algorithm(NaiveBayes("naive_bayes"))
    model_manager.add_algorithm(Svm("svm"))
    model_manager.add_algorithm(Feedforward("feedforward"))
    model_manager.add_algorithm(LogisticRegression("logistic_regression"))
    model_manager.add_algorithm(RandomForest("random_forest"))
    model_manager.add_algorithm(DecisionTree("decision_tree"))
    model_manager.add_algorithm(Lstm("lstm"))
