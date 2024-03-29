# This files contains the functions used by a random scheduler.
# The random scheduler chooses a random N and K pair that satisfies the reliability threshold.
# Then it randomly assignes the chunks to the sotrage nodes.

import itertools
import random
from drex.utils.tool_functions import reliability_thresold_met

# Return a pair N and K that matches the reliability trehsold
def random_schedule(number_of_nodes, reliability_threshold, reliability_of_nodes):
	
	pairs = []
	
	for i in range(2, number_of_nodes + 1): # Set of N
		for j in range(1, number_of_nodes - 1): # set of K
			if i > j: # N > K
				if (reliability_thresold_met(i, j, reliability_threshold, reliability_of_nodes)): # Reliability must be met
					pairs.append((i, j))
	
	if len(pairs) == 0:
		print("ERROR, no pair could be find to match the reliability threshold. Use a smaller value or change the set of storage nodes.")
		exit(1)
	
	random_index = random.randint(0, len(pairs) - 1)
	set_of_nodes_random_scheduler = list(range(0, number_of_nodes))
	while pairs[random_index][0] != len(set_of_nodes_random_scheduler):
		set_of_nodes_random_scheduler.pop(random.randrange(len(set_of_nodes_random_scheduler))) 
	
	return pairs[random_index][0], pairs[random_index][1], set_of_nodes_random_scheduler
