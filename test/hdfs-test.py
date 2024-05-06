from drex.schedulers.hdfs import *
from drex.schedulers.random import *
from drex.utils.hdfs.functions import split_data
import string


# Number of nodes
number_of_nodes = 10
set_of_nodes = list(range(0, number_of_nodes))

# File size in MB
file_size = 200

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
reliability_threshold = 0.99

set_of_nodes_chosen, N, K, node_sizes = hdfs_three_replications(
    number_of_nodes, reliability_threshold, p, node_sizes, file_size, bandwidths, "simulation")

data = ''.join(random.choices(string.ascii_letters + string.digits, k=file_size * 1024 * 1024))

blocks = split_data(data)

for b in blocks:
    print(len(b['block']))