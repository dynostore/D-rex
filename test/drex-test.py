import numpy as np
from drex.utils.load_data import RealRecords
from drex.utils.prediction import Predictor
from drex.utils.tool_functions import *
from drex.schedulers.random import *
from drex.schedulers.algorithm1 import *
from drex.schedulers.algorithm2 import *
from drex.schedulers.algorithm3 import *
from drex.schedulers.algorithm4 import *
import sys
import itertools

"""
Start of the inputs
"""

# Number of nodes
number_of_nodes = 10
print("There are", number_of_nodes, "nodes.")

# Numpy arrays of probability of failure each node over the data timeframe
p = []
for i in range(0, number_of_nodes):
    p.append(random.uniform(0.1, 0.15))

# Bandwidth to write on the storage nodes in MB/s
bandwidths = []
for i in range(0, number_of_nodes):
    bandwidths.append(random.uniform(10, 15))

# Storage size of each node
node_sizes = []  # Node sizes updated with data
total_node_size = 0
for i in range(0, number_of_nodes):
    node_sizes.append(random.uniform(600, 800))
    total_node_size += node_sizes[i]
max_node_size = max(node_sizes)

# Threshold we want to meet
reliability_threshold = 0.9

# To manage the real time obtained in experiments
real_records = RealRecords(dir_data="data/")

# File size in MB
file_size = 1
# TODO update this value when new data arrives in the system or if we have access to all data sizes
min_data_size = file_size

predictor = Predictor()  # Update for different file sizes

# We need to allow a maximum difference allowed to consider two nodes are similar
maximum_difference_allowed = 0.20  # 10%

"""
End of the inputs
"""

# for i in range(3, number_of_nodes):
# print(i,2,replication_and_chuncking_time(i, 2, file_size, bandwidths, real_records))
# replication_and_chuncking_time(i, 2, file_size, bandwidths, real_records)

"""
Algorithm 1
Time for 10 / 100 / 1000 nodes: 0 / 0 / 30 seconds
"""
# set_of_nodes_chosen, N, K, node_sizes = algorithm1(number_of_nodes, reliability_threshold, p, node_sizes, file_size)

"""
Algorithm 2
Time for 10 / 15 / 20 nodes: 0 / 18 / 835 seconds
"""
# set_of_nodes_chosen, N, K, node_sizes = algorithm2(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records, node_sizes)

"""
Algorithm 2 with reduced complexity: DOES NOT WORK
Time for 10 / 15 / 20 nodes: seconds
First need to declare the three variable here then you can loop over algorithm2_reduced_complexity
"""
# iteration = 0
# reduced_set_of_nodes = []
# for i in range (0, 10):
# set_of_nodes_chosen, N, K, node_sizes, iteration, reduced_set_of_nodes = algorithm2_reduced_complexity(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records, node_sizes, reduced_set_of_nodes, iteration, maximum_difference_allowed)

"""
Algorithm 3
Time for 10 / 15 / 20 nodes: 7 / 41 / seconds
"""
set_of_nodes_chosen, N, K, node_sizes = algorithm3(
    number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records, node_sizes, predictor)

"""
Algorithm 4
Time for 10 / 15 / 20 nodes: 4 / 35 / seconds
"""
set_of_nodes_chosen, N, K, node_sizes = algorithm4(number_of_nodes, p, bandwidths, reliability_threshold,
                                                   file_size, real_records, node_sizes, max_node_size, 
                                                   min_data_size, system_saturation, total_node_size, predictor)

# Random scheduler
"""
Random
Time for 10 / 15 / 20 nodes: 0 / 0 / 0 seconds
"""
# set_of_nodes_chosen, N, K, node_sizes = random_schedule(number_of_nodes, p, reliability_threshold, node_sizes, file_size)
