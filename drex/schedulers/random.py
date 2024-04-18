# This files contains the functions used by a random scheduler.
# The random scheduler chooses a random N and K pair that satisfies the reliability threshold.
# Then it randomly assignes the chunks to the sotrage nodes.

import itertools
import random
from drex.utils.tool_functions import reliability_thresold_met
import time, sys

# Return a pair N and K that matches the reliability threshold
def random_schedule(number_of_nodes, reliability_of_nodes, reliability_threshold):
	start = time.time()
	pairs = []
	set_of_nodes = list(range(0, number_of_nodes))
	reliability_of_nodes_chosen = []
	
	# ~ print("Set of nodes =", set_of_nodes)
	# ~ print("Reliability of nodes =", reliability_of_nodes)
	
	N = random.randint(2, number_of_nodes)
	K = random.randint(1, N - 1)
	# ~ print(N, K)
	set_of_nodes_chosen = random.sample(range(0, number_of_nodes), N)
	set_of_nodes_chosen.sort()
	# ~ print(set_of_nodes_chosen)
	for i in range(0, len(set_of_nodes_chosen)):
		reliability_of_nodes_chosen.append(reliability_of_nodes[set_of_nodes_chosen[i]])
	
	while (reliability_thresold_met(N, K, reliability_threshold, reliability_of_nodes) == False):	
		N = random.randint(2, number_of_nodes)
		K = random.randint(1, N - 1)
		# ~ print(N, K)
		set_of_nodes_chosen = random.sample(range(0, number_of_nodes), N)
		set_of_nodes_chosen.sort()
		# ~ print(set_of_nodes_chosen)
		for i in range(0, len(set_of_nodes_chosen)):
			reliability_of_nodes_chosen.append(reliability_of_nodes[set_of_nodes_chosen[i]])
	
	end = time.time()
	print("\nAlgorithm 3 chose N =", N, "and K =", K, "with the set of nodes:", set_of_nodes_chosen, "It took", end - start, "seconds.")
	return list(set_of_nodes_chosen), N, K