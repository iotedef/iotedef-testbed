# IoTEDef Testbed

This repository includes the source code of the IoTEDef system.

## Directories
* algorithms: the source codes of the classifiers
* analyzers: the source codes of the identification algorithm
* definitions: the source codes of the abstract model definitions
* encoders: the source codes of encoders
* features: 40 features are included
* modules: the modules of IoTEDef
* scripts: the scripts for the experiments and the graphs
* utils: other functions defined

## Tested environment
* Ubuntu 20.04
* Python 3.8.10

## Prerequisites
 * `sudo apt-get update && sudo apt-get install git python3-pip libpcap-dev tcpreplay`
 * `sudo pip3 install -r requirements.txt`

## How to Install
 * Make your root directory (e.g., mkdir ids-root)
 * Enter your root directory (e.g., cd ids-root)
 * git clone https://github.com/iotedef/iotedef-testbed.git
 * git clone https://github.com/iotedef/iotedef-dataset.git
 * Change the name of the dataset directory from iotedef-dataset to dataset (mv iotedef-dataset dataset)

## How to Run the IDS testbed
 * Run the infection identifier: python3 infection_identifier.py -c \<configuration file\> -o \<output file prefix\> -s \<serial number\> 
 * e.g., sudo python3 infection_identifier.py -c ids.conf -o infection_identifier -s 1
 * Run the IDS system (requires sudo privilege): sudo python3 ids.py -c \<configuration file\> -o \<output file prefix\> -s \<serial number\> -d \<dataset number\> -e \<dataset number\>
 * e.g., sudo python3 ids.py -c ids.conf -o ids -s 1 -d 1 -e 1

## How to Generate Dataset
 * The script `dataset/scripts/generate_dataset.py' is used to generate the datasets
 * You should generate a training set and a test set separately
 * You should generate the subdirectories under the dataset directory in the form of set_\<dataset number\> (the dataset number should be the positive number)
 * e.g., `mkdir set_2`
 * Please change the directory to the generated subdirectory (e.g., cd set_2)
 * Let's generate a training dataset
 * e.g., `python3 ../scripts/generate_dataset.py --benign ../specified/benign-large-1.pcap 0 10 --reconnaissance ../specified/portscanning-1-pkts.pcap 0 3 --benign ../specified/benign-telnet-1-pkts.pcap 2 1 --infection ../specified/bruteforce-small-1.pcap 4 2 --infection ../specified/bruteforce-small-2.pcap 5 2 --infection ../specified/bruteforce-small-3.pcap 6 2 --attack ../specified/mirai-udpflooding-1-pkts.pcap 9 1 -p training --local`
 * Let's generate a test dataset
 * e.g., `python3 ../scripts/generate_dataset.py --benign ../specified/benign-large-2.pcap 0 90 --reconnaissance ../specified/portscanning-3-pkts.pcap 0.5 1 --infection ../specified/infection-small-1.pcap 0.2 1 --benign ../specified/benign-telnet-test-2-pkts.pcap 0.7 1 --infection ../specified/infection-small-3.pcap 10 3 --benign ../specified/benign-telnet-test-4-pkts.pcap 15 3 --attack ../specified/mirai-udpflooding-2-pkts.pcap 78 2 -p test --local`
 * You can use the generated datasets by running the ids with the dataset number (e.g., `-d 2`)

## How to Add Algorithms
 * You can add a new detector algorithm to the algorithms directory by python3 add_algorithm.py --name \<name of a new algorithm\> (e.g., `python3 add_algorithm.py --name decision_tree`)
 * You can add a new infection identifier algorithm to the analyzers directory by python3 add_analyzer.py --name \<name of a new algorithm\> (e.g., `python3 add_analyzer.py --name attention`)
 * You can add a new encoding algorithm to the encoders directory by python3 add_encoder.py --name \<name of a new encoder\> (e.g., `python3 add_encoder.py --name identity`)
 * You can add a new feature to the features directory by python3 add_feature.py --type \<flow/packet\> --name \<name of a new feature\> (e.g., `python3 add_feature.py --type flow --name iat`)
 * Please update a new setting by `python3 prepare_ids.py` when you add something

## Configurations

### Parameters
 * Window Size: the time length of the window (e.g., 1 second): integer
 * Sliding Window: whether the sliding window is applied: True/False
 * Episode Maximum Length: the number of windows in one episode: integer
 * Episode Minimum Frequency: the minimum frequency of the pattern occurrence: float
 * Episode Minimum Confidence: the probability of the patter occurrence: float
 * Fixed Length Episode: whether we consider only the fixed length of the episode: True/False
 * Batch Granularity: the granularity of the batch in seconds: float
 * Batch Width: the length of the batch: integer
 * Classes: the classes that we consider in our analysis: characters
 * Home Directory: the home directory of the result files: string
 * Round Value: the decimal points that is rounded off: integer
 * IP Address: the IP address of the infection identifier: string
 * Port: the port number of the infection identifier: integer
 * Output Prefix: the prefix of the detection output file: string
 * Analysis Result Prefix: the prefix of the analysis output file: string
 * Number Of Candidates: the number of candidates that the episode-tree-based algorithm considers: integer
 * Number Of Results: the number of results that the episode-tree-based algorithm maintains per each loop: integer
 * Number Of Final Results: the number of results that the episode-tree-based algorithm outputs: integer
 * Local: whether the experiments run locally or not: True/False
 * IP Address 0: the IP address of the first machine when two machines are used in the testbed as a sender and a receiver: string
 * Port 0: the port number of the first machine: integer
 * IP Address 1: the IP address of the second machine when two machines are used in the testbed as a sender and a receiver: string
 * Port 1: the port number of the second machine: integer
 * Self Evolving: whether the self-evolving is supported: True/False
 * Update Strategy: the update strategy algorithm: 1/2/3

### Encoders
 * Encoder: the encoder algorithm: string

### Detectors
 * Attack Detection: the classifier algorithm for the attack: string
 * Infection Detection: the classifier algorithm for the infection: string
 * Reconnaissance Detection: the classifier algorithm for the reconnaissance: string

### Infection Identifier
 * Analyzer: the infection identification algorithm: string

### Flow Features
 * forward_iat_std: the standard deviation of the inter-arrival time in the forward direction: True/False
 * flow_iat_total: the total inter-arrival time in the flow per window: True/False
 * flow_rst: the total number of the RST flags enabled in the flow per window: True/False
 * forward_iat_max: the maximum inter-arrival time of the flow per window: True/False
 * flow_packets_per_second: the number of packets per second of the flow per window: True/False
 * forward_packet_length_mean: the mean of the packet length in the forward direction: True/False
 * backward_packet_length_std: the standard deviation of the packet length in the backward direction: True/False
 * flow_ece: the total number of the ECE flags enabled in the flow per window: True/False
 * flow_iat_mean: the mean of the inter-arrival time in the flow per window: True/False
 * backward_packet_length_mean: the mean of the packet length in the backward direction: True/False
 * forward_packet_length_min: the minimum of the packet length in the forward direction: True/False
 * forward_iat_total: the total inter-arrival time in the forward direction: True/False
 * backward_packet_length_min: the minimum of the packet length in the backward direction: True/False
 * backward_iat_mean: the mean of the inter-arrival time in the backward direction: True/False
 * flow_cwr: the total number of the CWR flags enabled in the flow per window: True/False
 * flow_iat_min: the minimum of the inter-arrival time: True/False
 * flow_iat_max: the maximum of the inter-arrival time: True/False
 * total_length_of_backward_packets: the total length of the packets in the backward direction: True/False
 * forward_packet_length_std: the standard deviation of the packet length in the forward direction: True/False
 * total_backward_packets: the total number of packets in the backward direction: True/False
 * backward_iat_total: the total inter-arrival time in the backward direction: True/False
 * total_length_of_forward_packets: the total length of the packets in the forward direction: True/False
 * bpkts_per_second: the number of packets per second in the backward direction: True/False
 * backward_iat_std: the standard deviation of the inter-arrival time in the backward direction: True/False
 * forward_packet_length_max: the maximum of the packet length in the forward direction: True/False
 * fpkts_per_second: the number of packets per second in the forward direction: True/False
 * total_fhlen: the total number of header length in the forward direction: True/False
 * forward_iat_mean: the mean of the inter-arrival time in the forward direction: True/False
 * flow_urg: the total number of the URG flags enabled in the flow per window: True/False
 * flow_ack: the total number of the ACK flags enabled in the flow per window: True/False
 * forward_iat_min: the minimum of the inter-arrival time in the forward direction: True/False
 * flow_iat_std: the standard deviation of the inter-arrival time: True/False
 * total_forward_packets: the total number of packets in the forward direction: True/False
 * flow_syn: the number of the SYN flags enabled in the flow per window: True/False
 * flow_psh: the number of the PSH flags enabled in the flow per window: True/False
 * total_bhlen: the total number of the header length in the backward direction: True/False
 * flow_fin: the number of the FIN flags enabled in the flow per window: True/False
 * backward_packet_length_max: the maximum of the packet length in the backward direction: True/False
 * backward_iat_max: the maximum of the inter-arrival time in the backward direction: True/False
 * backward_iat_min: the minimum of the inter-arrival time in the backward direction: True/False
 * flow_protocol: the protocol value of the flow: True/False
