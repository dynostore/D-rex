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
# ~ number_of_nodes = 12

# Numpy arrays of probability of failure each node over the data timeframe
# ~ p = np.array([0.01, 0.2, 0.1, 0.1, 0.1, 0.3, 0.1, 0.01, 0.5, 0.6])
p = [0.1] * number_of_nodes

# Bandwidth to write on the storage nodes in MB/s
bandwidths = [20] * number_of_nodes

# Threshold we want to meet
reliability_threshold = 0.6

# To manage the real time obtained in experiments
real_records = RealRecords(dir_data="data/")

# File size in MB
file_size = 10

# Test for invalid values
if (file_size <= 0 or number_of_nodes < 3):
	print("ERROR: invalid value for file_size and/or number_of_nodes")
	exit(1)

#k = 2
#for i in range(3, number_of_nodes):
#	print(i,i-2,replication_and_chuncking_time(i, 2, file_size, bandwidths[:i], real_records))

# Algorithm 1
# Time for 10 nodes: 0.0008
# Time for 100 nodes: 0.0351
# Time for 1000 nodes: 11.1834
# ~ algorithm1(number_of_nodes, reliability_threshold, p)

# Algorithm 2
# Time for 10 nodes: 0.1598
# Time for 15 nodes: 7.0923
# Time for 17 nodes: 35.6570
# Time for 19 nodes: 132.0603
# Time for 20 nodes: 279.5449
# Time for 22 nodes: 1280.2816
# ~ algorithm2(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records)

# Algorithm 3
algorithm3(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records)

# Random scheduler
# ~ N, K, set_of_nodes_random_scheduler = random_schedule(N, reliability_threshold, p)
# ~ print("")
# ~ print("Random scheduler chose N =", N, "and K =", K, "with the set of nodes:", set_of_nodes_random_scheduler)
