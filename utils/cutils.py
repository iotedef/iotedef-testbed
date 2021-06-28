import sys
sys.path.append("..")
from analyzers.attention import Attention
from analyzers.identity import Identity
from analyzers.baseline import Baseline
from analyzers.viterbi import Viterbi
from analyzers.simple_attention import SimpleAttention
from analyzers.episode_tree import EpisodeTree
from analyzers.bilstm_attention import BilstmAttention

def init_analyzers(causal_analyzer):
    causal_analyzer.add_analyzer(Attention("attention"))
    causal_analyzer.add_analyzer(Identity("identity"))
    causal_analyzer.add_analyzer(Baseline("baseline"))
    causal_analyzer.add_analyzer(Viterbi("viterbi"))
    causal_analyzer.add_analyzer(SimpleAttention("simple_attention"))
    causal_analyzer.add_analyzer(EpisodeTree("episode_tree"))
    causal_analyzer.add_analyzer(BilstmAttention("bilstm_attention"))
