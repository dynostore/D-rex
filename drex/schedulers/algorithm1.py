from drex.utils.tool_functions import *
import time

def algorithm1(number_of_nodes, reliability_threshold, reliability_of_nodes, node_sizes, file_size):
	"""
	Return the full set of nodes and choose K as big as possible
	"""
	
	start = time.time()
	
	N = number_of_nodes
	K = get_max_K_from_reliability_threshold_and_nodes_chosen(N, reliability_threshold, reliability_of_nodes)
	
	if (K == -1):
		print("ERROR: No K was found for Algorithm 1.")
		exit(1)

	set_of_nodes = list(range(0, number_of_nodes))
	
	for i in set_of_nodes:
		if (node_sizes[i] - (file_size/K) < 0):
			print("ERROR: Algorithm 1 could not find a solution that would not overflow the memory of the nodes")
			exit(1)
		
	node_sizes = update_node_sizes(set_of_nodes, K, file_size, node_sizes)
	
	end = time.time()
	
	print("\nAlgorithm 1 chose N =", N, "and K =", K, "with the set of nodes:", set_of_nodes, "It took", end - start, "seconds.")
	
	return set_of_nodes, N, K, node_sizes
