# To use: python3 tool_functions.py

from poibin import PoiBin
import numpy as np
import sys

# Return the estimated time cost of chunking and replicating a data of 
# size file_size into N chunks of size file_size/K
# uses an interpolation or extrapolation from previous experiments
# TODO in future works: update estimation with observation from current 
# execution
# Takes as inputs N, K, the size of the file and the bandwidth to write on the storage nodes
# Return a time in seconds (or micro-seconds?)
def replication_and_chuncking_time(N, K, file_size, bandwidths):
	time = 1
	return time

# ~ # Faster than is_pareto_efficient_simple, but less readable.
# ~ def is_pareto_efficient(costs, return_mask = True):
    # ~ """
    # ~ Find the pareto-efficient points
    # ~ :param costs: An (n_points, n_costs) array
    # ~ :param return_mask: True to return a mask
    # ~ :return: An array of indices of pareto-efficient points.
        # ~ If return_mask is True, this will be an (n_points, ) boolean array
        # ~ Otherwise it will be a (n_efficient_points, ) integer array of indices.
    # ~ """
    # ~ is_efficient = np.arange(costs.shape[0])
    # ~ n_points = costs.shape[0]
    # ~ next_point_index = 0  # Next index in the is_efficient array to search for
    # ~ while next_point_index<len(costs):
        # ~ nondominated_point_mask = np.any(costs<costs[next_point_index], axis=1)
        # ~ nondominated_point_mask[next_point_index] = True
        # ~ is_efficient = is_efficient[nondominated_point_mask]  # Remove dominated points
        # ~ costs = costs[nondominated_point_mask]
        # ~ next_point_index = np.sum(nondominated_point_mask[:next_point_index])+1
    # ~ if return_mask:
        # ~ is_efficient_mask = np.zeros(n_points, dtype = bool)
        # ~ is_efficient_mask[is_efficient] = True
        # ~ return is_efficient_mask
    # ~ else:
        # ~ return is_efficient

# Getting the set of N on the pareto front that match the reliability threshold
def get_set_of_N_on_pareto_front(number_of_nodes, reliability_threshold, reliability_of_nodes, file_size, bandwidths):
	N_on_pareto = []
	set_of_possible_N_and_K_couple = []
	space_cost_of_couple = []
	time_cost_of_couple = []
	
	# First we get the set of N and their associating K as big as possible that meet the resilience threshold
	for i in range (1, number_of_nodes + 1):
		K = get_max_K_from_reliability_threshold_and_nodes(i, reliability_threshold, reliability_of_nodes)
		if (K != -1): # This value of N can match the reliability threshold
			set_of_possible_N_and_K_couple.append((i, K))
	
	print("set_of_possible_N_and_K_couple:", set_of_possible_N_and_K_couple)
	
	# Put in a table the time and space cost of each couple of possible N,K
		
	for i in range (0, len(set_of_possible_N_and_K_couple)):
		space_cost_of_couple.append((file_size/set_of_possible_N_and_K_couple[i][1])*set_of_possible_N_and_K_couple[i][0]) # (file_size/K)*N
		time_cost_of_couple.append(replication_and_chuncking_time(set_of_possible_N_and_K_couple[i][0], set_of_possible_N_and_K_couple[i][1], file_size, bandwidths))
	
	print(space_cost_of_couple)
	print(time_cost_of_couple)
		
	# time_cost = interpolation from Dante function

	
	# Then we get from the possible couple the set of N that is on the pareto front
	
	
	return N_on_pareto

# Getting the biggest K we can have to still meet the reliability threshold. If no K is found that match the reliability, -1 is return meaning that the value N is not sufficiant to meet the reliability threshold
def get_max_K_from_reliability_threshold_and_nodes(number_of_nodes, reliability_threshold, reliability_of_nodes):
	# Gettin Poisson Binomial distributions
	pb = PoiBin(reliability_of_nodes)
	max_K = -1
	
	for i in range (1, number_of_nodes):
		K = i
	
		# Setting number of failures we can withstand
		x = number_of_nodes - K
	
		print("With N =", number_of_nodes, "and K =", K, "the probability of availability is", pb.cdf(x))
	
		if (pb.cdf(x) > reliability_threshold):
			max_K = K

	if max_K == -1:
		print("No value of K can meet the reliability threshold with N =", number_of_nodes)
	else:
		print("Biggest K we can choose to meet the reliability threshold with N =", number_of_nodes, "is", max_K)
	
	return max_K


# Under are just some values and examples on how to use the utils functions

# Numpy arrays of probability of failure each node over the data timeframe
p = np.array([0.01, 0.2, 0.1, 0.1, 0.1, 0.3])

# Bandwidth to write on the storage nodes in MB/s
bandwidths = np.array([10, 23, 15, 13, 11, 32])

# Number of replica we create
N = 6

# Threshold we want to meet
reliability_threshold = 0.99

# File size in MB
file_size = 10

print("Probability of availability must be superior to", reliability_threshold)

K = get_max_K_from_reliability_threshold_and_nodes(N, reliability_threshold, p)

set_of_N_on_pareto = get_set_of_N_on_pareto_front(N, reliability_threshold, p, file_size, bandwidths)
print("The set of N on the pareto front between speed and size is", set_of_N_on_pareto)
