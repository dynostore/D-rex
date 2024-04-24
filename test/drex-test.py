import numpy as np
from drex.utils.load_data import RealRecords
from drex.utils.tool_functions import *
from drex.schedulers.random import *
from drex.schedulers.algorithm1 import *
from drex.schedulers.algorithm2 import *
from drex.schedulers.algorithm3 import *
from drex.schedulers.algorithm4 import *
import sys
import itertools

# Under are just some values and examples on how to use the utils functions
# TODO have these values as external input by the user

# Number of nodes
number_of_nodes = 10
print("There are", number_of_nodes, "nodes.")

# Numpy arrays of probability of failure each node over the data timeframe
# p = np.array([0.1, 0.2, 0.1, 0.1, 0.1, 0.3, 0.1, 0.1, 0.5, 0.2])
# p = [0.1] * number_of_nodes
p = []
for i in range(0, number_of_nodes):
	p.append(random.uniform(0.1, 0.15))

# Bandwidth to write on the storage nodes in MB/s
# bandwidths = np.array([20, 10, 15, 18, 21, 20, 20, 10, 20, 10])
# bandwidths = [20] * number_of_nodes
bandwidths = []
for i in range(0, number_of_nodes):
	bandwidths.append(random.uniform(10, 15))

# Storage size of each node
# node_sizes = np.array([100, 100, 100, 100, 200, 120, 160, 190, 120, 100])
# node_sizes = [100] * number_of_nodes
node_sizes = [] # Node sizes updated with data
total_node_size = 0
for i in range(0, number_of_nodes):
	node_sizes.append(random.uniform(100, 1000))
	total_node_size += node_sizes[i]
max_node_size = max(node_sizes)

# Threshold we want to meet
reliability_threshold = 0.9

# To manage the real time obtained in experiments
real_records = RealRecords(dir_data="data/")

# File size in MB
file_size = 100
min_data_size = file_size # TODO update this value when new data arrives in te system or if we have access to all data sizes

#We need to allow a maximum difference allowed to consider two nodes are similar
maximum_difference_allowed = 0.10 # 10%

# Test for invalid values
if (file_size <= 0 or number_of_nodes < 3):
	print("ERROR: invalid value for file_size and/or number_of_nodes")
	exit(1)

#for i in range(3, number_of_nodes):
#	print(i,2,replication_and_chuncking_time(i, 2, file_size, bandwidths, real_records))
	#replication_and_chuncking_time(i, 2, file_size, bandwidths, real_records)

# Algorithm 1
# Time for 10 / 100 / 1000 nodes: 0 / 0 / 11 seconds
# set_of_nodes_chosen, N, K = algorithm1(number_of_nodes, reliability_threshold, p, node_sizes, file_size)

# Algorithm 2
# Time for 10 / 15 / 20 nodes: 0 / 18 / 835 seconds
# set_of_nodes_chosen, N, K = algorithm2(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records, node_sizes)


# For reduced complexity we need to call this function that groups similar nodes together
matrix_of_differences = group_nodes_by_similarities(number_of_nodes, p, bandwidths, node_sizes, maximum_difference_allowed)

# Getting the reduced set of nodes
reduced_set_of_nodes, reduced_set_of_nodes_first_nodes_only = get_reduced_set_of_nodes(number_of_nodes, matrix_of_differences, maximum_difference_allowed)

set_of_nodes_chosen, N, K = algorithm2_reduced_complexity(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records, node_sizes, reduced_set_of_nodes, reduced_set_of_nodes_first_nodes_only)

# Algorithm 3
# Time for 16 nodes: 16 seconds
# Time for 20 nodes: 333 seconds
# set_of_nodes_chosen, N, K = algorithm3(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records)

# Algorithm 4
# ~ set_of_nodes_chosen, N, K = algorithm4(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records, node_sizes, max_node_size, min_data_size, system_saturation, total_node_size)

# Random scheduler
# set_of_nodes_chosen, N, K = random_schedule(number_of_nodes, p, reliability_threshold)
