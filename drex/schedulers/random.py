# This files contains the functions used by a random scheduler.
# The random scheduler chooses a random N and K pair that satisfies the reliability threshold.
# Then it randomly assignes the chunks to the sotrage nodes.

import itertools
import random
from drex.utils.tool_functions import *
import time, sys

def get_random_excluding_exclusions(number_of_nodes, already_looked_at, node_sizes):
    valid_choices = set(range(2, number_of_nodes + 1)) - already_looked_at
    if not valid_choices:
        # ~ print("No random valid choices available")
        return -1
    return random.choice(list(valid_choices))
    
# Return a pair N and K that matches the reliability threshold
def random_schedule(number_of_nodes, reliability_of_nodes, reliability_threshold, node_sizes, file_size):
	"""
	Random N, K and set of nodes
	"""
	
	start = time.time()
	
	pairs = []
	set_of_nodes = list(range(0, number_of_nodes))
	reliability_of_nodes_chosen = []
	
	already_looked_at = set()
	solution_found = False
	
	while solution_found == False:
		N = get_random_excluding_exclusions(number_of_nodes, already_looked_at, node_sizes)
		if N == -1:
			return -1, -1, -1, node_sizes
		already_looked_at.add(N)
		# ~ print("Try N=", N)
		K = random.randint(1, N - 1)
		set_of_nodes_chosen = random.sample(range(0, number_of_nodes), N)
		set_of_nodes_chosen.sort()

		reliability_of_nodes_chosen = [reliability_of_nodes[node] for node in set_of_nodes_chosen]
					
		while (reliability_thresold_met(N, K, reliability_threshold, reliability_of_nodes) == False):	
			N = random.randint(2, number_of_nodes)
			K = random.randint(1, N - 1)
			set_of_nodes_chosen = random.sample(range(0, number_of_nodes), N)
			set_of_nodes_chosen.sort()
			for i in range(0, len(set_of_nodes_chosen)):
				reliability_of_nodes_chosen.append(reliability_of_nodes[set_of_nodes_chosen[i]])
		
		if (nodes_can_fit_new_data(set_of_nodes_chosen, node_sizes, file_size/K) == True):
			solution_found = True
			# ~ print("Random could not find a solution that does not overflow the memory")
			# ~ return -1, -1, -1, node_sizes
		
	node_sizes = update_node_sizes(set_of_nodes_chosen, K, file_size, node_sizes)
	
	end = time.time()
	
	# ~ print("\nRandom chose N =", N, "and K =", K, "with the set of nodes:", set_of_nodes_chosen, "It took", end - start, "seconds.")
	
	return list(set_of_nodes_chosen), N, K, node_sizes
