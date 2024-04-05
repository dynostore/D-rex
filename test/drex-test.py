import numpy as np
from drex.utils.load_data import RealRecords
from drex.utils.tool_functions import get_max_K_from_reliability_threshold_and_nodes_chosen, is_pareto_efficient, get_set_of_node_associated_with_chosen_N_and_K, replication_and_chuncking_time
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

# Numpy arrays of probability of failure each node over the data timeframe
# ~ p = np.array([0.01, 0.2, 0.1, 0.1, 0.1, 0.3])
p = [0.1] * number_of_nodes

# Bandwidth to write on the storage nodes in MB/s
bandwidths = [20] * number_of_nodes

# Threshold we want to meet
reliability_threshold = 0.9

# To manage the real time obtained in experiments
real_records = RealRecords(dir_data="data/")

# File size in MB
file_size = 10

# Algorithm 1
# Time for 10 nodes: 0.0008
# Time for 100 nodes: 0.0351
# Time for 1000 nodes: 11.1834
algorithm1(number_of_nodes, reliability_threshold, p)

# Algorithm 2
algorithm2(number_of_nodes, p, bandwidths, reliability_threshold, file_size, real_records)

# ~ # Algorithm 3
# ~ # 1. Get set of N, K and associated nodes that match the reliability and put them in a list, with fastest N when multiple set of nodes can staisfy the reliability
# ~ min_K = 0
# ~ set_of_nodes_chosen = []
# ~ set_of_nodes = list(range(0, number_of_nodes))
# ~ set_of_possible_solutions = []
# ~ time_and_space_from_set_of_possible_solution = []
# ~ for i in range(2, number_of_nodes + 1):
	# ~ min_time = sys.maxsize
	# ~ for set_of_nodes_chosen in itertools.combinations(set_of_nodes, i):
		# ~ reliability_of_nodes_chosen = []
		# ~ bandwidth_of_nodes_chosen = []
		# ~ for j in range(0, len(set_of_nodes_chosen)):
			# ~ reliability_of_nodes_chosen.append(p[set_of_nodes_chosen[j]])
			# ~ bandwidth_of_nodes_chosen.append(bandwidths[set_of_nodes_chosen[j]])
		# ~ K = get_max_K_from_reliability_threshold_and_nodes_chosen(i, reliability_threshold, reliability_of_nodes_chosen)
		# ~ if (K != -1):
			# ~ time = replication_and_chuncking_time(i, K, file_size, bandwidth_of_nodes_chosen, real_records)
			# ~ set_of_possible_solutions.append((i, K, set_of_nodes_chosen, time, (file_size/K)*i))
			# ~ time_and_space_from_set_of_possible_solution.append([time, (file_size/K)*i])

# ~ # 2. Take those that are on the pareto front
# ~ costs = np.asarray(time_and_space_from_set_of_possible_solution)
# ~ test = is_pareto_efficient(costs, False)
# ~ print("Set on pareto front is", test)
# ~ print(set_of_possible_solutions[test[0]])
# ~ print(set_of_possible_solutions[test[1]])
# ~ # 3. Plateau

# ~ # 4. Results
# ~ print("")
# ~ print("Algorithm 3 chose N =", min_N, "and K =", min_K, "with the set of nodes:", min_set_of_nodes_chosen)


# ~ # Random scheduler
# ~ N, K, set_of_nodes_random_scheduler = random_schedule(N, reliability_threshold, p)
# ~ print("")
# ~ print("Random scheduler chose N =", N, "and K =", K, "with the set of nodes:", set_of_nodes_random_scheduler)
