import numpy as np
from drex.utils.load_data import RealRecords
from drex.utils.prediction import Predictor
from drex.utils.tool_functions import *
from drex.schedulers.random import *
from drex.schedulers.algorithm1 import *
from drex.schedulers.algorithm2 import *
from drex.schedulers.algorithm3 import *
from drex.schedulers.algorithm4 import *
from drex.schedulers.hdfs import *
import sys
import itertools

"""
Start of the inputs
"""

# Number of nodes
number_of_nodes = 10
set_of_nodes = list(range(0, number_of_nodes))
print("There are", number_of_nodes, "nodes.")

# Numpy arrays of probability of failure each node over the data timeframe
p = []
for i in range(0, number_of_nodes):
    p.append(random.uniform(0.1, 0.15))
# ~ p = [0.1, 0.8, 0.7, 0.9, 0.9, 0.05, 0.9, 0.8, 0.9, 0.9]

# Bandwidth to write on the storage nodes in MB/s
bandwidths = []
for i in range(0, number_of_nodes):
    bandwidths.append(random.uniform(10, 15))

# Storage size of each node in B
node_sizes = []  # Node sizes updated with data
total_node_size = 0
for i in range(0, number_of_nodes):
    node_sizes.append(random.uniform(600, 800)*1024*1024)
    total_node_size += node_sizes[i]
max_node_size = max(node_sizes)

# Threshold we want to meet
reliability_threshold = 0.99

# To manage the real time obtained in experiments
real_records = RealRecords(dir_data="data/")

# File size in MB
file_size = 5
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
# ~ set_of_nodes_chosen, N, K, node_sizes = algorithm1(number_of_nodes, reliability_threshold, p, node_sizes, file_size)

"""
Algorithm 2
Time for 10 / 15 / 20 nodes: 0 / 18 / 835 seconds
"""
# ~ set_of_nodes_chosen, N, K, node_sizes = algorithm2(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records, node_sizes, predictor)

"""
Algorithm 2 with reduced complexity by grouping node by similarities: DOES NOT WORK
Time for 10 / 15 / 20 nodes: seconds
First need to declare the three variable here then you can loop over algorithm2_reduced_complexity
"""
# iteration = 0
# reduced_set_of_nodes = []
# for i in range (0, 10):
# set_of_nodes_chosen, N, K, node_sizes, iteration, reduced_set_of_nodes = algorithm2_group_node_by_similarities(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records, node_sizes, reduced_set_of_nodes, iteration, maximum_difference_allowed, predictor)

"""
Algorithm 2 with reduced complexity by working on less nodes
Time for 55 nodes: 0.22 seconds
"""
# ~ set_of_nodes_chosen, N, K, node_sizes = algorithm2_work_with_reduced_set_of_nodes(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records, node_sizes, predictor)

"""
Algorithm 3
Time for 10 / 15 / 20 nodes: 7 / 41 / seconds
"""
# ~ set_of_nodes_chosen, N, K, node_sizes = algorithm3(
    # ~ number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records, node_sizes, predictor)

"""
Algorithm 3 with reduced complexity by looking at less posibilities
Time for 100 nodes: 8 seconds
"""
# ~ set_of_nodes_chosen, N, K, node_sizes = algorithm3_look_at_reduced_set_of_possibilities(
    # ~ number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records, node_sizes, predictor)

"""
Algorithm 4
Time for 10 / 15 nodes: 4 / 35 seconds
"""
# ~ set_of_nodes_chosen, N, K, node_sizes = algorithm4(number_of_nodes, p, bandwidths, reliability_threshold,
                                                   # ~ file_size, real_records, node_sizes, max_node_size, 
                                                   # ~ min_data_size, system_saturation, total_node_size, predictor)

"""
Algorithm 4 with reduced complexity by looking at less posibilities
Time for 100 nodes: 8.47 seconds
"""
# ~ set_of_nodes_chosen, N, K, node_sizes = algorithm4_look_at_reduced_set_of_possibilities(number_of_nodes, p, bandwidths, reliability_threshold,
                                                   # ~ file_size, real_records, node_sizes, max_node_size, 
                                                   # ~ min_data_size, system_saturation, total_node_size, predictor)

# Random scheduler
"""
Random
Time for 10 / 15 / 20 nodes: 0 / 0 / 0 seconds
"""
# ~ set_of_nodes_chosen, N, K, node_sizes = random_schedule(number_of_nodes, p, reliability_threshold, node_sizes, file_size)

"""
HDFS replicate everything three times
Time for 100 nodes: 0 seconds
"""
# ~ set_of_nodes_chosen, N, K, node_sizes = hdfs_three_replications(number_of_nodes, reliability_threshold, p, node_sizes, file_size, bandwidths, "simulation")
# ~ set_of_nodes_chosen, node_sizes, size_to_remove_from_nodes = hdfs_three_replications(number_of_nodes, reliability_threshold, p, node_sizes, file_size, bandwidths, "real")

"""
HDFS with Reed-Solomon
RS1 and RS2 corresponds the value in RS(x,y) meaning that for RS1 data block 
you have RS2 parity blocks
Please provide a mode being either "simulation" or "real" to indicate if you want the 
real value of K (a float) or a rounded value for real experiments (an integer)
Time for 100 nodes: seconds
"""
# ~ RS1 = 10
# ~ RS2 = 4
# ~ RS1 = 6
# ~ RS2 = 3
RS1 = 6
RS2 = 3
set_of_nodes_chosen, N, K, node_sizes, size_to_remove_from_nodes = hdfs_reed_solomon(number_of_nodes, reliability_threshold, p, node_sizes, file_size, bandwidths, RS1, RS2)
