import sys
sys.path.append("..")
from analyzers.episode_tree import EpisodeTree
from analyzers.identity import Identity
from analyzers.baseline import Baseline
from analyzers.simple_attention import SimpleAttention
from analyzers.viterbi import Viterbi
from analyzers.seq2seq_attention import Seq2seqAttention
from analyzers.bilstm_attention import BilstmAttention
from analyzers.attention import Attention

def init_analyzers(causal_analyzer):
    causal_analyzer.add_analyzer(EpisodeTree("episode_tree"))
    causal_analyzer.add_analyzer(Identity("identity"))
    causal_analyzer.add_analyzer(Baseline("baseline"))
    causal_analyzer.add_analyzer(SimpleAttention("simple_attention"))
    causal_analyzer.add_analyzer(Viterbi("viterbi"))
    causal_analyzer.add_analyzer(Seq2seqAttention("seq2seq_attention"))
    causal_analyzer.add_analyzer(BilstmAttention("bilstm_attention"))
    causal_analyzer.add_analyzer(Attention("attention"))
