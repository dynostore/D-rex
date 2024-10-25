from drex.utils.tool_functions import *
import time

def algorithm1(number_of_nodes, reliability_threshold, reliability_of_nodes, node_sizes, file_size):
	"""
	Return the full set of nodes and choose K as big as possible
	When a noee can't be used cause full, it just reduces N while it fits.
	"""

	set_of_nodes = list(range(0, number_of_nodes))
    
	# Combine nodes and sizes into tuples
	combined = list(zip(set_of_nodes, node_sizes))

	# Sort the combined list of tuples by bandwidth
	sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)  # Sort by the second element (sizes)

	# Unpack the sorted tuples into separate lists
	sorted_nodes_by_sorted_sizes, sorted_sizes = zip(*sorted_combined)
	# ~ N = number_of_nodes
	N = 0
	
	for N in range (number_of_nodes, 2, -1):
		
		set_of_nodes_chosen = list(sorted_nodes_by_sorted_sizes[:N])
		reliability_of_nodes_chosen = [reliability_of_nodes[node] for node in set_of_nodes_chosen]

		K = get_max_K_from_reliability_threshold_and_nodes_chosen(N, reliability_threshold, reliability_of_nodes_chosen)

		if (K != -1):		
			found = True
		
			for i in set_of_nodes_chosen:
				if (node_sizes[i] - (file_size/K) < 0):
					found = False
				
			if found == True:
				node_sizes = update_node_sizes(set_of_nodes_chosen, K, file_size, node_sizes)
				return set_of_nodes_chosen, N, K, node_sizes

	
	# ~ print("Algorithm 1 could not find a solution that would not overflow the memory of the nodes after looking at all N > 1")
	return -1, -1, -1, node_sizes
