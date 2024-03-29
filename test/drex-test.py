import numpy as np
from drex.utils.load_data import RealRecords
from drex.utils.tool_functions import get_max_K_from_reliability_threshold_and_nodes, get_set_of_N_on_pareto_front

# Under are just some values and examples on how to use the utils functions

# Numpy arrays of probability of failure each node over the data timeframe
# TODO use real values and have them as external inputs
p = np.array([0.01, 0.2, 0.1, 0.1, 0.1, 0.3])

# Bandwidth to write on the storage nodes in MB/s
# TODO use real values and have them as external inputs
bandwidths = np.array([10, 23, 15, 13, 11, 32])

# Number of nodes
# TODO have it as external input
N = 6

# Threshold we want to meet
# TODO have it as external input
reliability_threshold = 0.99

# To manage the real time obtained in experiments
real_records = RealRecords(dir_data="data/")

# File size in MB
# TODO have it as external input and have different values depending on the data type
file_size = 10

print("Probability of availability must be superior to", reliability_threshold)


K = get_max_K_from_reliability_threshold_and_nodes(N, reliability_threshold, p)

set_of_N_on_pareto = get_set_of_N_on_pareto_front(N, reliability_threshold, p, file_size, bandwidths, real_records)
print("The set of N on the pareto front between speed and size is", set_of_N_on_pareto)