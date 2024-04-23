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
# ~ number_of_nodes = 100
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
print(node_sizes)
max_node_size = max(node_sizes)

# Threshold we want to meet
reliability_threshold = 0.9

# To manage the real time obtained in experiments
real_records = RealRecords(dir_data="data/")

# File size in MB
file_size = 100
min_data_size = file_size # TODO update this value when new data arrives in te system or if we have access to all data sizes

# Test for invalid values
if (file_size <= 0 or number_of_nodes < 3):
	print("ERROR: invalid value for file_size and/or number_of_nodes")
	exit(1)

#for i in range(3, number_of_nodes):
#	print(i,2,replication_and_chuncking_time(i, 2, file_size, bandwidths, real_records))
	#replication_and_chuncking_time(i, 2, file_size, bandwidths, real_records)

# For reduced complexity we need to call this function that groups similar nodes together
matrix_of_differences = group_nodes_by_similarities(number_of_nodes, p, bandwidths, node_sizes)

#We need to allow a maximum difference allowed to consider two nodes are similar
maximum_difference_allowed = 0.10 # Here it is 10%

# Then we get a reduced set of nodes from this
reduced_set_of_nodes, reduced_set_of_nodes_first_nodes_only = get_reduced_set_of_nodes(number_of_nodes, matrix_of_differences, maximum_difference_allowed)

system_saturation = system_saturation(node_sizes, min_data_size, total_node_size)
print("Saturation of the system is", system_saturation)

# Example usage of exponential for algorithm 4
# ~ x1 = 100 # max node
# ~ y1 = 1
# ~ x2 = 10 # min data
# ~ y2 = 1/number_of_nodes
# ~ x = 11  # Remaining data after adding chunk
# ~ result = exponential_function(x, x1, y1, x2, y2)
# ~ print(f"f({x}) = {result}")

# By hand it is:
# ~ f(x) = ab^x
# ~ ab^100 = 1 -> a = b^-100 -> a = 0.077459322
# ~ ab^10 = 0.1 ->  b^-100*b^10 = 0.1 -> b^-90 = 0.1 -> b = 1.02591

# Algorithm 1
# Time for 10 nodes: 0 seconds
# Time for 100 nodes: 0 seconds
# Time for 1000 nodes: 11 seconds
# set_of_nodes_chosen, N, K = algorithm1(number_of_nodes, reliability_threshold, p)

# Algorithm 2 vs Algorithm 2 reduced complexity 10% and ranges are [0.1, 0.15][10, 15][100, 150]
# Time for 10 nodes: 0 seconds | 0 seconds
# Time for 15 nodes: 7 seconds | 0 seconds
# Time for 17 nodes: 35 seconds | 0 seconds
# Time for 19 nodes: 132 seconds | 0 seconds
# Time for 20 nodes: 279 seconds | 0 seconds
# Time for 22 nodes: 1280 seconds
# set_of_nodes_chosen, N, K = algorithm2(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records)
# set_of_nodes_chosen, N, K = algorithm2_reduced_complexity(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records, reduced_set_of_nodes_first_nodes_only)

# Algorithm 3
# Time for 16 nodes: 16 seconds
# Time for 20 nodes: 333 seconds
# set_of_nodes_chosen, N, K = algorithm3(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records)

# Algorithm 4
set_of_nodes_chosen, N, K = algorithm4(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records, node_sizes, max_node_size, min_data_size, system_saturation)

# Random scheduler
# set_of_nodes_chosen, N, K = random_schedule(number_of_nodes, p, reliability_threshold)

# Update node sizes with what was chosen
node_sizes = update_node_sizes(set_of_nodes_chosen, K, file_size, node_sizes)
