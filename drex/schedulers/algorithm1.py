from drex.utils.tool_functions import *
import time

def algorithm1(number_of_nodes, reliability_threshold, reliability_of_nodes):
	start = time.time()
	N = number_of_nodes
	K = get_max_K_from_reliability_threshold_and_nodes_chosen(N, reliability_threshold, reliability_of_nodes)
	if (N == -1):
		print("ERROR: No N was found for Algorithm 1.")
		exit(1)
	set_of_nodes = list(range(0, number_of_nodes))
	end = time.time()
	print("\nAlgorithm 1 chose N =", N, "and K =", K, "with the set of nodes:", set_of_nodes, "It took", end - start, "seconds.")
	return set_of_nodes, N, K
