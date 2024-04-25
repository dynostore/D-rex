import numpy as np
from drex.utils.load_data import RealRecords
from drex.utils.tool_functions import replication_and_chuncking_time, get_max_K_from_reliability_threshold_and_nodes_chosen, is_pareto_efficient, get_set_of_node_associated_with_chosen_N_and_K, replication_and_chuncking_time
from drex.schedulers.random import *
from drex.schedulers.algorithm1 import *
from drex.schedulers.algorithm2 import *
from drex.schedulers.algorithm3 import *
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
node_sizes = []
for i in range(0, number_of_nodes):
	node_sizes.append(random.uniform(100, 150))

# Threshold we want to meet
reliability_threshold = 0.6

# To manage the real time obtained in experiments
real_records = RealRecords(dir_data="data/")

# File size in MB
file_size = 100

# Test for invalid values
if (file_size <= 0 or number_of_nodes < 3):
	print("ERROR: invalid value for file_size and/or number_of_nodes")
	exit(1)
 
#print(2,1,replication_and_chuncking_time(2, 1, file_size, bandwidths, real_records))
#for i in range(3, number_of_nodes):
#	print(i,2,replication_and_chuncking_time(i, 2, file_size, bandwidths, real_records))
	#replication_and_chuncking_time(i, 2, file_size, bandwidths, real_records)

# For reduced complexity we need to call this function that groups similar nodes together
matrix_of_differences = group_nodes_by_similarities(number_of_nodes, p, bandwidths, node_sizes)

#We need to allow a maximum difference allowed to consider two nodes are similar
maximum_difference_allowed = 0.10 # Here it is 10%

# Then we get a reduced set of nodes from this
reduced_set_of_nodes, reduced_set_of_nodes_first_nodes_only = get_reduced_set_of_nodes(number_of_nodes, matrix_of_differences, maximum_difference_allowed)

# Algorithm 1
# Time for 10 nodes: 0 seconds
# Time for 100 nodes: 0 seconds
# Time for 1000 nodes: 11 seconds
# ~ algorithm1(number_of_nodes, reliability_threshold, p)

# Algorithm 2 vs Algorithm 2 reduced complexity 10% and ranges are [0.1, 0.15][10, 15][100, 150]
# Time for 10 nodes: 0 seconds | 0 seconds
# Time for 15 nodes: 7 seconds | 0 seconds
# Time for 17 nodes: 35 seconds | 0 seconds
# Time for 19 nodes: 132 seconds | 0 seconds
# Time for 20 nodes: 279 seconds | 0 seconds
# Time for 22 nodes: 1280 seconds
algorithm2(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records)
# algorithm2_reduced_complexity(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records, reduced_set_of_nodes_first_nodes_only)

# Algorithm 3
# Time for 16 nodes: 16 seconds
# Time for 20 nodes: 333 seconds
algorithm3(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records)

# Random scheduler
# random_schedule(number_of_nodes, p, reliability_threshold)
