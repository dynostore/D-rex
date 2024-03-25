# To use: python3 tool_functions.py

from poibin import PoiBin
import numpy as np
import sys

# Getting the set of N on the pareto front that match the reliability threshold
def get_set_of_N_on_pareto_front(number_of_nodes, reliability_threshold, reliability_of_nodes):
	N_on_pareto = []
	
	
	return N_on_pareto

# Getting the biggest K we can have to still meet the reliability threshold
def get_max_K_from_reliability_threshold_and_nodes(number_of_nodes, reliability_threshold, reliability_of_nodes):
	# Gettin Poisson Binomial distributions
	pb = PoiBin(reliability_of_nodes)
		
	for i in range (1, number_of_nodes - 1):
		K = i
	
		# Setting number of failures we can withstand
		x = number_of_nodes - K
	
		# Getting cumulative distribution function
		print("With N =", number_of_nodes, "and K =", K, "the probability of availability is", pb.cdf(x))
	
		if (pb.cdf(x) > reliability_threshold):
			max_K = K
	
	return max_K

# Numpy arrays of probability of failure each node over the data timeframe
p = np.array([0.01, 0.2, 0.1, 0.1, 0.1, 0.3])

# Number of replica we create
N = 6

# Threshold we want to meet
reliability_threshold = 0.99

print("Probability of availability must be superior to", reliability_threshold)

K = get_max_K_from_reliability_threshold_and_nodes(N, reliability_threshold, p)
print("Biggest K we can choose to meet the reliability threshold is", K)
