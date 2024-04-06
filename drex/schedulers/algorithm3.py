from drex.utils.tool_functions import *
import time, sys, numpy

def algorithm3(number_of_nodes, reliability_of_nodes, bandwidths, reliability_threshold, file_size, real_records):
	start = time.time()	
	# 1. Get set of N, K and associated nodes that match the reliability and put them in a list, with fastest N when multiple set of nodes can staisfy the reliability
	min_K = 0
	set_of_nodes_chosen = []
	set_of_nodes = list(range(0, number_of_nodes))
	set_of_possible_solutions = []
	# ~ set_of_possible_solutions = 
	time_and_space_from_set_of_possible_solution = []
	for i in range(2, number_of_nodes + 1):
		min_time = sys.maxsize
		for set_of_nodes_chosen in itertools.combinations(set_of_nodes, i):
			reliability_of_nodes_chosen = []
			bandwidth_of_nodes_chosen = []
			for j in range(0, len(set_of_nodes_chosen)):
				reliability_of_nodes_chosen.append(reliability_of_nodes[set_of_nodes_chosen[j]])
				bandwidth_of_nodes_chosen.append(bandwidths[set_of_nodes_chosen[j]])
			K = get_max_K_from_reliability_threshold_and_nodes_chosen(i, reliability_threshold, reliability_of_nodes_chosen)
			if (K != -1):
				replication_and_write_time = replication_and_chuncking_time(i, K, file_size, bandwidth_of_nodes_chosen, real_records)
				set_of_possible_solutions.append((i, K, set_of_nodes_chosen, replication_and_write_time, (file_size/K)*i))
				time_and_space_from_set_of_possible_solution.append([replication_and_write_time, (file_size/K)*i])

	# 2. Take those that are on the pareto front
	costs = numpy.asarray(time_and_space_from_set_of_possible_solution)
	test = is_pareto_efficient(costs, False)
	print("Set on pareto front is", test)

	a = []
	for i in range (0, len(test)):
		a.append(time_and_space_from_set_of_possible_solution[test[i]][0])
	
	# 3. Finding the solution on the plateau
	# get max from a
	# get min from a
	# start from smallest time and stop when 10% degradation of time has been made and keep the index
	# ~ a = numpy.percentile(costs[:,3], 90)
	# ~ print(a)
	
	exit(1)

	end = time.time()
	print("\nAlgorithm 3 chose N =", min_N, "and K =", min_K, "with the set of nodes:", min_set_of_nodes_chosen, "It took", end - start, "seconds.")
