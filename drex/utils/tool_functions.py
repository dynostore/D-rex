# To use: python3 tool_functions.py

from drex.utils.poibin import PoiBin
import numpy as np
import sys
from drex.utils.load_data import RealRecords
import itertools

# Return the estimated time cost of chunking and replicating a data of 
# size file_size into N chunks of size file_size/K
# uses an interpolation or extrapolation from previous experiments
# TODO in future works: update estimation with observation from current 
# execution
# Takes as inputs N, K, the size of the file and the bandwidth to write on the storage nodes
# Return a time in seconds (or micro-seconds?)
def replication_and_chuncking_time(n, k, file_size, bandwidths, real_records):
    sizes_times = []
    for s,d in zip(real_records.sizes, real_records.data):
        result_filter = d[(d["n"] == n) & (d["k"] == k)]
        if len(result_filter) > 0:
            sizes_times.append([s, result_filter[0]['avg_time']])
    sizes_times = np.array(sizes_times)
    if file_size >= min(real_records.sizes) and file_size <= max(real_records.sizes):
        print("Interpolating")
        return np.interp(file_size, sizes_times[:,0], sizes_times[:,1])
    else: #Extrapolate
        print("Extrapolating")
        fit = np.polyfit(sizes_times[:,0], sizes_times[:,1] ,1)
        line = np.poly1d(fit)
        return line(file_size)
	#return 1
 
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
# TODO MAXIME: finish this function
def get_set_of_N_on_pareto_front(number_of_nodes, reliability_threshold, reliability_of_nodes, file_size, bandwidths, real_records):
	N_on_pareto = []
	set_of_possible_N_and_K_couple = []
	space_cost_of_couple = []
	time_cost_of_couple = []
	
	# First we get the set of N and their associated K as big as possible that meet the resilience threshold
	# TODO: this is wrong as we need to send the right set of reliability, have to fix it
	for i in range (1, number_of_nodes + 1):
		K = get_max_K_from_reliability_threshold_and_nodes_chosen(i, reliability_threshold, reliability_of_nodes)
		if (K != -1): # Means that this value of N cannot match the reliability threshold
			set_of_possible_N_and_K_couple.append((i, K))
	
	if (len(set_of_possible_N_and_K_couple) == 0):
		print("ERROR: No value of N is available to meet the reliability thresold.")
		exit
	print("set_of_possible_N_and_K_couple:", set_of_possible_N_and_K_couple)
	
	# Put in a table the time and space cost of each couple of possible N,K
	for i in range (0, len(set_of_possible_N_and_K_couple)):
		space_cost_of_couple.append((file_size/set_of_possible_N_and_K_couple[i][1])*set_of_possible_N_and_K_couple[i][0]) # (file_size/K)*N
		time_cost_of_couple.append(replication_and_chuncking_time(set_of_possible_N_and_K_couple[i][0], set_of_possible_N_and_K_couple[i][1], file_size, bandwidths, real_records))
	
	print(space_cost_of_couple)
	print(time_cost_of_couple)
	
	# Then we get from the possible couple the set of N that is on the pareto front
	
	
	return N_on_pareto

# Return True or false
# Must indicate the reliability of teh set of nodes used! Not all the nodes
def reliability_thresold_met(N, K, reliability_threshold, reliability_of_nodes):
	pb = PoiBin(reliability_of_nodes)
	x = N - K
	if (pb.cdf(x) >= reliability_threshold):
		return True
	else:
		return False

# Getting the biggest K we can have to still meet the reliability threshold.
# If no K is found that match the reliability, -1 is returned meaning that
# the value of N is not sufficiant to meet the reliability threshold
# Careful, number_of_nodes and reliability_of_nodes must be the set of nodes
# you inted to use.
def get_max_K_from_reliability_threshold_and_nodes_chosen(number_of_nodes, reliability_threshold, reliability_of_nodes):
	# Gettin Poisson Binomial distributions
	max_K = -1
	
	for i in range (1, number_of_nodes):
		K = i
		if (reliability_thresold_met(number_of_nodes, K, reliability_threshold, reliability_of_nodes)):
			max_K = K
	
	if max_K == -1:
		print("/!\ No value of K can meet the reliability threshold with N =", number_of_nodes, "/!\ ")
	
	return max_K

def get_set_of_node_associated_with_chosen_N_and_K(number_of_nodes, N, K, reliability_threshold, reliability_of_nodes):
	set_of_nodes = list(range(0, number_of_nodes))
	reliability_of_nodes_chosen = []
	set_of_nodes_chosen = []
	
	for set_of_nodes_chosen in itertools.combinations(set_of_nodes, N):
		reliability_of_nodes_chosen = []
		for i in range(0, len(set_of_nodes_chosen)):
			reliability_of_nodes_chosen.append(reliability_of_nodes[set_of_nodes_chosen[i]])
		if (reliability_thresold_met(N, K, reliability_threshold, reliability_of_nodes_chosen)): 
			return(set_of_nodes_chosen)
			
	print("/!\ CRITICAL ERROR: No set of nodes returned in get_set_of_node_associated_with_chosen_N_and_K. This is not normal. /!\ ")
	exit(1)