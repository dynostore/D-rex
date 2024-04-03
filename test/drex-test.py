import numpy as np
from drex.utils.load_data import RealRecords
from drex.utils.tool_functions import get_max_K_from_reliability_threshold_and_nodes_chosen, get_set_of_N_on_pareto_front
from drex.schedulers.random import random_schedule
from drex.utils.tool_functions import replication_and_chuncking_time
from drex.utils.tool_functions import get_set_of_node_associated_with_chosen_N_and_K
import sys

# Under are just some values and examples on how to use the utils functions

# Numpy arrays of probability of failure each node over the data timeframe
# TODO use real values and have them as external inputs
p = np.array([0.01, 0.2, 0.1, 0.1, 0.1, 0.3])

# Bandwidth to write on the storage nodes in MB/s
# TODO use real values and have them as external inputs
bandwidths = np.array([10, 23, 15, 13, 11, 32])

# Number of nodes
# TODO have it as external input
number_of_nodes = 6

# Threshold we want to meet
# TODO have it as external input
reliability_threshold = 0.99

# To manage the real time obtained in experiments
real_records = RealRecords(dir_data="data/")

# File size in MB
# TODO have it as external input and have different values depending on the data type
file_size = 10

set_of_N_on_pareto = get_set_of_N_on_pareto_front(number_of_nodes, reliability_threshold, p, file_size, bandwidths, real_records)

# Algorithm 1
N = number_of_nodes
K = get_max_K_from_reliability_threshold_and_nodes_chosen(N, reliability_threshold, p)
set_of_nodes = list(range(0, number_of_nodes))
print("")
print("Algorithm 1 chose N =", N, "and K =", K, "with the set of nodes:", set_of_nodes)

# Algorithm 2
min_time = sys.maxsize
min_N = 0
min_K = 0
for i in range(2, number_of_nodes + 1):
	K = get_max_K_from_reliability_threshold_and_nodes_chosen(i, reliability_threshold, p)
	if (K != -1):
		time = replication_and_chuncking_time(i, K, file_size, bandwidths, real_records)
		if time < min_time:
			min_time = time
			min_N = i
			min_K = K
N = min_N
K = min_K
set_of_nodes = get_set_of_node_associated_with_chosen_N_and_K(number_of_nodes, N, K, reliability_threshold, p)
print("")
print("Algorithm 2 chose N =", min_N, "and K =", min_K, "with the set of nodes:", set_of_nodes)

# Algorithm 3

# Random scheduler
N, K, set_of_nodes_random_scheduler = random_schedule(N, reliability_threshold, p)
print("")
print("Random scheduler chose N =", N, "and K =", K, "with the set of nodes:", set_of_nodes_random_scheduler)
