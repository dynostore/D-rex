# This files contains the functions used by a random scheduler.
# The random scheduler chooses a random N and K pair that satisfies the reliability threshold.
# Then it randomly assignes the chunks to the sotrage nodes.

import itertools
import random
from drex.utils.tool_functions import reliability_thresold_met

# Return a pair N and K that matches the reliability threshold
def random_schedule(number_of_nodes, reliability_threshold, reliability_of_nodes):
	print("")
	print("### Random Scheduler ###")
	pairs = []
	set_of_nodes = list(range(0, number_of_nodes))
	reliability_of_nodes_chosen = []
	print("Set of nodes =", set_of_nodes)
	print("Reliability of nodes =", reliability_of_nodes)
	
	for i in range(2, number_of_nodes + 1): # Set of N
		for j in range(1, i): # Set of K and N > K
			print("Testing N =", i, "and K =", j)
			if i == number_of_nodes: # Reliability must be met with a certain set of nodes. Here we use all nodes so no change
				# ~ print("i == number_of_nodes")
				if (reliability_thresold_met(i, j, reliability_threshold, reliability_of_nodes)):
					pairs.append((i, j, set_of_nodes))
			else: # Reliability must be met with a certain subset of nodes chosen
				# ~ for reliability_of_nodes_chosen in itertools.combinations(reliability_of_nodes, i):
				for set_of_nodes_chosen in itertools.combinations(set_of_nodes, i):
					reliability_of_nodes_chosen = []
					# ~ print("Subset of nodes =", set_of_nodes_chosen)
					for k in range(0, len(set_of_nodes_chosen)):
						reliability_of_nodes_chosen.append(reliability_of_nodes[set_of_nodes_chosen[k]])
					# ~ print("Associated reliability = ", reliability_of_nodes_chosen)
					if (reliability_thresold_met(i, j, reliability_threshold, reliability_of_nodes_chosen)): 
						pairs.append((i, j, set_of_nodes_chosen))
	
	print(pairs)
	if len(pairs) == 0:
		print("ERROR, no pair could be find to match the reliability threshold. Use a smaller value or change the set of storage nodes.")
		exit(1)
	
	random_index = random.randint(0, len(pairs) - 1)
	
	return pairs[random_index][0], pairs[random_index][1], pairs[random_index][2], 
