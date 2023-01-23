import sys
sys.path.append("..")
from features.flow.forward_iat_total import ForwardIatTotal
from features.flow.backward_iat_std import BackwardIatStd
from features.flow.backward_iat_max import BackwardIatMax
from features.flow.total_fhlen import TotalFhlen
from features.flow.total_bhlen import TotalBhlen
from features.flow.backward_iat_min import BackwardIatMin
from features.flow.forward_iat_min import ForwardIatMin
from features.flow.fpkts_per_second import FpktsPerSecond
from features.flow.flow_iat_min import FlowIatMin
from features.flow.forward_packet_length_mean import ForwardPacketLengthMean
from features.flow.forward_iat_std import ForwardIatStd
from features.flow.flow_iat_total import FlowIatTotal
from features.flow.flow_syn import FlowSyn
from features.flow.flow_fin import FlowFin
from features.flow.forward_iat_max import ForwardIatMax
from features.flow.flow_iat_max import FlowIatMax
from features.flow.forward_packet_length_min import ForwardPacketLengthMin
from features.flow.total_backward_packets import TotalBackwardPackets
from features.flow.flow_iat_mean import FlowIatMean
from features.flow.flow_ece import FlowEce
from features.flow.flow_protocol import FlowProtocol
from features.flow.flow_iat_std import FlowIatStd
from features.flow.bpkts_per_second import BpktsPerSecond
from features.flow.backward_packet_length_mean import BackwardPacketLengthMean
from features.flow.backward_iat_mean import BackwardIatMean
from features.flow.total_length_of_forward_packets import TotalLengthOfForwardPackets
from features.flow.flow_cwr import FlowCwr
from features.flow.flow_packets_per_second import FlowPacketsPerSecond
from features.flow.forward_iat_mean import ForwardIatMean
from features.flow.flow_urg import FlowUrg
from features.flow.total_length_of_backward_packets import TotalLengthOfBackwardPackets
from features.flow.flow_rst import FlowRst
from features.flow.total_forward_packets import TotalForwardPackets
from features.flow.forward_packet_length_max import ForwardPacketLengthMax
from features.flow.flow_ack import FlowAck
from features.flow.forward_packet_length_std import ForwardPacketLengthStd
from features.flow.backward_iat_total import BackwardIatTotal
from features.flow.backward_packet_length_max import BackwardPacketLengthMax
from features.flow.flow_psh import FlowPsh
from features.flow.backward_packet_length_std import BackwardPacketLengthStd
from features.flow.backward_packet_length_min import BackwardPacketLengthMin

def init_features(feature_extractor):
    feature_extractor.add_feature(ForwardIatTotal("forward_iat_total"))
    feature_extractor.add_feature(BackwardIatStd("backward_iat_std"))
    feature_extractor.add_feature(BackwardIatMax("backward_iat_max"))
    feature_extractor.add_feature(TotalFhlen("total_fhlen"))
    feature_extractor.add_feature(TotalBhlen("total_bhlen"))
    feature_extractor.add_feature(BackwardIatMin("backward_iat_min"))
    feature_extractor.add_feature(ForwardIatMin("forward_iat_min"))
    feature_extractor.add_feature(FpktsPerSecond("fpkts_per_second"))
    feature_extractor.add_feature(FlowIatMin("flow_iat_min"))
    feature_extractor.add_feature(ForwardPacketLengthMean("forward_packet_length_mean"))
    feature_extractor.add_feature(ForwardIatStd("forward_iat_std"))
    feature_extractor.add_feature(FlowIatTotal("flow_iat_total"))
    feature_extractor.add_feature(FlowSyn("flow_syn"))
    feature_extractor.add_feature(FlowFin("flow_fin"))
    feature_extractor.add_feature(ForwardIatMax("forward_iat_max"))
    feature_extractor.add_feature(FlowIatMax("flow_iat_max"))
    feature_extractor.add_feature(ForwardPacketLengthMin("forward_packet_length_min"))
    feature_extractor.add_feature(TotalBackwardPackets("total_backward_packets"))
    feature_extractor.add_feature(FlowIatMean("flow_iat_mean"))
    feature_extractor.add_feature(FlowEce("flow_ece"))
    feature_extractor.add_feature(FlowProtocol("flow_protocol"))
    feature_extractor.add_feature(FlowIatStd("flow_iat_std"))
    feature_extractor.add_feature(BpktsPerSecond("bpkts_per_second"))
    feature_extractor.add_feature(BackwardPacketLengthMean("backward_packet_length_mean"))
    feature_extractor.add_feature(BackwardIatMean("backward_iat_mean"))
    feature_extractor.add_feature(TotalLengthOfForwardPackets("total_length_of_forward_packets"))
    feature_extractor.add_feature(FlowCwr("flow_cwr"))
    feature_extractor.add_feature(FlowPacketsPerSecond("flow_packets_per_second"))
    feature_extractor.add_feature(ForwardIatMean("forward_iat_mean"))
    feature_extractor.add_feature(FlowUrg("flow_urg"))
    feature_extractor.add_feature(TotalLengthOfBackwardPackets("total_length_of_backward_packets"))
    feature_extractor.add_feature(FlowRst("flow_rst"))
    feature_extractor.add_feature(TotalForwardPackets("total_forward_packets"))
    feature_extractor.add_feature(ForwardPacketLengthMax("forward_packet_length_max"))
    feature_extractor.add_feature(FlowAck("flow_ack"))
    feature_extractor.add_feature(ForwardPacketLengthStd("forward_packet_length_std"))
    feature_extractor.add_feature(BackwardIatTotal("backward_iat_total"))
    feature_extractor.add_feature(BackwardPacketLengthMax("backward_packet_length_max"))
    feature_extractor.add_feature(FlowPsh("flow_psh"))
    feature_extractor.add_feature(BackwardPacketLengthStd("backward_packet_length_std"))
    feature_extractor.add_feature(BackwardPacketLengthMin("backward_packet_length_min"))
