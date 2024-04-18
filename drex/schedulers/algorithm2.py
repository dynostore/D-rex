from drex.utils.tool_functions import *
import sys, time

def algorithm2(number_of_nodes, reliability_of_nodes, bandwidths, reliability_threshold, file_size, real_records):
	start = time.time()	
	min_time = sys.maxsize
	min_N = 0
	min_K = 0
	set_of_nodes_chosen = []
	set_of_nodes = list(range(0, number_of_nodes))
	for i in range(3, number_of_nodes + 1):		
		for set_of_nodes_chosen in itertools.combinations(set_of_nodes, i):
			reliability_of_nodes_chosen = []
			bandwidth_of_nodes_chosen = []
			for j in range(0, len(set_of_nodes_chosen)):
				reliability_of_nodes_chosen.append(reliability_of_nodes[set_of_nodes_chosen[j]])
				bandwidth_of_nodes_chosen.append(bandwidths[set_of_nodes_chosen[j]])
			K = get_max_K_from_reliability_threshold_and_nodes_chosen(i, reliability_threshold, reliability_of_nodes_chosen)
			# ~ print("Test", i, K, set_of_nodes_chosen)
			if (K != -1):
				replication_and_write_time = replication_and_chuncking_time(i, K, file_size, bandwidth_of_nodes_chosen, real_records)
				# ~ print(replication_and_write_time)
				if (replication_and_write_time < min_time):
					min_time = replication_and_write_time
					min_N = i
					min_K = K
					min_set_of_nodes_chosen = set_of_nodes_chosen
	end = time.time()
	print("\nAlgorithm 2 chose N =", min_N, "and K =", min_K, "with the set of nodes:", min_set_of_nodes_chosen, "It took", end - start, "seconds.")
	return list(min_set_of_nodes_chosen), min_N, min_K
