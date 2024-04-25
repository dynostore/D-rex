# To use: python3 tool_functions.py

from drex.utils.poibin import PoiBin
import numpy as np
import math
import sys
from drex.utils.load_data import RealRecords

import itertools
from scipy.interpolate import interp1d
from scipy.interpolate import Rbf
from scipy.interpolate import LinearNDInterpolator

def calculate_transfer_time(data_size, bandwidth):
    """
    Calculate the estimated transfer time given data size and bandwidth.
    
    Args:
    data_size (float): Size of data to be transferred, in bits.
    bandwidth (float): Bandwidth of the connection, in bits per second.
    
    Returns:
    float: Estimated transfer time in seconds.
    """
    transfer_time = data_size / bandwidth
    return transfer_time


def my_interpolation(sizes_arr, ns_arr, ks_arr, times_arr):
    """CT interpolator + nearest-neighbor extrapolation.

    Parameters
    ----------
    xy : ndarray, shape (npoints, ndim)
        Coordinates of data points
    z : ndarray, shape (npoints)
        Values at data points

    Returns
    -------
    func : callable
        A callable object which mirrors the CT behavior,
        with an additional neareast-neighbor extrapolation
        outside of the data range.
    """
    f = LinearNDInterpolator(list(zip(sizes_arr, ns_arr, ks_arr)), times_arr)

    # this inner function will be returned to a user
    def new_f(size, n, k):
        # evaluate the CT interpolator. Out-of-bounds values are nan.
        zz = f(size, n, k)
        if np.isnan(zz):
            zz = 0
            f2 =  Rbf(sizes_arr, ns_arr, ks_arr, times_arr, function="linear", smooth=5)
            zz = f2(size, n, k)
        #print(zz)
        #nans = np.isnan(zz)

        """if nans.any():
            # for each nan point, find its nearest neighbor
            inds = np.argmin(
                (sizes_arr[:, None] - xx[nans])**2 +
                (ns_arr[:, None] - yy[nans])**2 +
                (ks_arr[:, None] - yy[nans])**2
                , axis=0)
            # ... and use its value
            zz[nans] = z[inds]
        return zz"""
        return zz

    return new_f

# Return the estimated time cost of chunking and replicating a data of 
# size file_size into N chunks of size file_size/K
# uses an interpolation or extrapolation from previous experiments
# TODO in future works: update estimation with observation from current 
# execution
# Takes as inputs N, K, the size of the file and the bandwidth to write on the storage nodes
# Return a time in seconds (or micro-seconds?)
def replication_and_chuncking_time(n, k, file_size, bandwidths, real_records):
    chunk_size = file_size / k
    sizes_times = []
    
    
    # Case 1: We have values of n and k in the real_records
    number_sizes = 0
    for s in real_records.sizes:
        
        d = real_records.data_dict[s]
        result_filter = d[(d["n"] == n) & (d["k"] == k)]
        if len(result_filter) > 0:
            for b in bandwidths:
                sizes_times.append([s, result_filter[0]['avg_time'] + calculate_transfer_time(file_size, b)])
            sizes_times.append([s, result_filter[0]['avg_time']])
            number_sizes += 1
    
    transfer_time_per_chunk = calculate_transfer_time(chunk_size, max(bandwidths))
    if len(sizes_times) > 0 and number_sizes > 1:
        sizes_times = np.array(sizes_times)
        interp_func = interp1d(sizes_times[:,0], sizes_times[:,1], fill_value="extrapolate")
        chunking_time = interp_func(file_size)
        """if file_size >= min(sizes_times[:,0]) and file_size <= max(sizes_times[:,0]):
            # ~ print("Interpolating")
            #chunking_time = np.interp(file_size, sizes_times[:,0], sizes_times[:,1])
            interp_func = interp1d(sizes_times[:,0], sizes_times[:,1])
            chunking_time = interp_func(file_size)
        else: #Extrapolate
            # ~ print("Extrapolating")
            fit = np.polyfit(sizes_times[:,0], sizes_times[:,1] ,1)
            line = np.poly1d(fit)
            chunking_time = line(file_size)"""
        return chunking_time + transfer_time_per_chunk
    else:
        #Find two nearest values in size
        ns_arr = []
        ks_arr = []
        times_arr = []
        sizes_arr = []
        vals_abs = np.argsort([abs(x-file_size) for x in real_records.sizes])
        #Get values
        for idx in vals_abs:
            ns = real_records.data_dict[real_records.sizes[idx]]["n"][:]
            ks = real_records.data_dict[real_records.sizes[idx]]["k"][:]
            times = real_records.data_dict[real_records.sizes[idx]]["avg_time"][:]
            sizes = [real_records.sizes[idx]] * len(ns)
            ns_arr.extend(ns)
            ks_arr.extend(ks)
            times_arr.extend(times)
            sizes_arr.extend(sizes)
        #Interpolate
        interp = my_interpolation(
            sizes_arr, ns_arr, ks_arr, times_arr
        )
        res = interp(file_size, n, k)
        return res + transfer_time_per_chunk
    
# Return the estimated time cost of chunking and replicating a data of 
# size file_size into N chunks of size file_size/K
# uses an interpolation or extrapolation from previous experiments
# TODO in future works: update estimation with observation from current 
# execution
# Takes as inputs N, K, the size of the file and the bandwidth to write on the storage nodes
# Return a time in seconds (or micro-seconds?)
def replication_and_chuncking_time_v0(n, k, file_size, bandwidths, real_records):
    chunk_size = file_size / k
    sizes_times = []
    for s,d in zip(real_records.sizes, real_records.data):
        result_filter = d[(d["n"] == n) & (d["k"] == k)]
        if len(result_filter) > 0:
            #for b in bandwidths:
            #    sizes_times.append([s, result_filter[0]['avg_time'] + calculate_transfer_time(file_size, b)])
            sizes_times.append([s, result_filter[0]['avg_time']])
    #print(sizes_times)
    sizes_times = np.array(sizes_times)
    if file_size >= min(real_records.sizes) and file_size <= max(real_records.sizes):
        # ~ print("Interpolating")
        #chunking_time = np.interp(file_size, sizes_times[:,0], sizes_times[:,1])
        interp_func = interp1d(sizes_times[:,0], sizes_times[:,1])
        chunking_time = interp_func(file_size)
    else: #Extrapolate
        # ~ print("Extrapolating")
        fit = np.polyfit(sizes_times[:,0], sizes_times[:,1] ,1)
        line = np.poly1d(fit)
        chunking_time = line(file_size)
    transfer_time_per_chunk = calculate_transfer_time(chunk_size, max(bandwidths))
    #transfer_time_per_chunk = calculate_transfer_time(file_size, max(bandwidths))
    return chunking_time + transfer_time_per_chunk
    
    
    # Case 1: We have values of n and k in the real_records
    number_sizes = 0
    for s in real_records.sizes:
        
        d = real_records.data_dict[s]
        result_filter = d[(d["n"] == n) & (d["k"] == k)]
        if len(result_filter) > 0:
            for b in bandwidths:
                sizes_times.append([s, result_filter[0]['avg_time'] + calculate_transfer_time(file_size, b)])
            sizes_times.append([s, result_filter[0]['avg_time']])
            number_sizes += 1
    
    transfer_time_per_chunk = calculate_transfer_time(chunk_size, max(bandwidths))
    if len(sizes_times) > 0 and number_sizes > 1:
        sizes_times = np.array(sizes_times)
        interp_func = interp1d(sizes_times[:,0], sizes_times[:,1], fill_value="extrapolate")
        chunking_time = interp_func(file_size)
        """if file_size >= min(sizes_times[:,0]) and file_size <= max(sizes_times[:,0]):
            # ~ print("Interpolating")
            #chunking_time = np.interp(file_size, sizes_times[:,0], sizes_times[:,1])
            interp_func = interp1d(sizes_times[:,0], sizes_times[:,1])
            chunking_time = interp_func(file_size)
        else: #Extrapolate
            # ~ print("Extrapolating")
            fit = np.polyfit(sizes_times[:,0], sizes_times[:,1] ,1)
            line = np.poly1d(fit)
            chunking_time = line(file_size)"""
        return chunking_time + transfer_time_per_chunk
    else:
        #Find two nearest values in size
        ns_arr = []
        ks_arr = []
        times_arr = []
        sizes_arr = []
        vals_abs = np.argsort([abs(x-file_size) for x in real_records.sizes])
        #Get values
        for idx in vals_abs:
            ns = real_records.data_dict[real_records.sizes[idx]]["n"][:]
            ks = real_records.data_dict[real_records.sizes[idx]]["k"][:]
            times = real_records.data_dict[real_records.sizes[idx]]["avg_time"][:]
            sizes = [real_records.sizes[idx]] * len(ns)
            ns_arr.extend(ns)
            ks_arr.extend(ks)
            times_arr.extend(times)
            sizes_arr.extend(sizes)
        #Interpolate
        interp = my_interpolation(
            sizes_arr, ns_arr, ks_arr, times_arr
        )
        res = interp(file_size, n, k)
        return res + transfer_time_per_chunk
    
# Faster than is_pareto_efficient_simple, but less readable.
def is_pareto_efficient(costs, return_mask = True):
    """
    Find the pareto-efficient points
    :param costs: An (n_points, n_costs) array
    :param return_mask: True to return a mask
    :return: An array of indices of pareto-efficient points.
        If return_mask is True, this will be an (n_points, ) boolean array
        Otherwise it will be a (n_efficient_points, ) integer array of indices.
    """
    is_efficient = np.arange(costs.shape[0])
    n_points = costs.shape[0]
    next_point_index = 0  # Next index in the is_efficient array to search for
    while next_point_index<len(costs):
        nondominated_point_mask = np.any(costs<costs[next_point_index], axis=1)
        nondominated_point_mask[next_point_index] = True
        is_efficient = is_efficient[nondominated_point_mask]  # Remove dominated points
        costs = costs[nondominated_point_mask]
        next_point_index = np.sum(nondominated_point_mask[:next_point_index])+1
    if return_mask:
        is_efficient_mask = np.zeros(n_points, dtype = bool)
        is_efficient_mask[is_efficient] = True
        return is_efficient_mask
    else:
        return is_efficient

# Must indicate the reliability of the set of nodes used. Not  of all the nodes
def reliability_thresold_met(N, K, reliability_threshold, reliability_of_nodes):
	pb = PoiBin(reliability_of_nodes)
	x = N - K
	if (pb.cdf(x) >= reliability_threshold):
		return True
	else:
		return False

# Getting the biggest K we can have to still meet the reliability threshold.
# If no K is found that match the reliability, -1 is returned meaning that
# the value of N is not sufficiant to meet the reliability threshold
# Careful, number_of_nodes and reliability_of_nodes must be the number and 
# reliability of the set of nodes you inted to use.
def get_max_K_from_reliability_threshold_and_nodes_chosen(number_of_nodes, reliability_threshold, reliability_of_nodes):
	max_K = -1
	for i in range (1, number_of_nodes):
		K = i
		if (reliability_thresold_met(number_of_nodes, K, reliability_threshold, reliability_of_nodes)):
			max_K = K
	# ~ if max_K == -1:
		# ~ print("/!\ No value of K can meet the reliability threshold with N =", number_of_nodes, "/!\ ")
	return max_K

def get_set_of_node_associated_with_chosen_N_and_K(number_of_nodes, N, K, reliability_threshold, reliability_of_nodes):
	set_of_nodes = list(range(0, number_of_nodes))
	reliability_of_nodes_chosen = []
	set_of_nodes_chosen = []
	
	for set_of_nodes_chosen in itertools.combinations(set_of_nodes, N):
		reliability_of_nodes_chosen = []
		for i in range(0, len(set_of_nodes_chosen)):
			reliability_of_nodes_chosen.append(reliability_of_nodes[set_of_nodes_chosen[i]])
		if (reliability_thresold_met(N, K, reliability_threshold, reliability_of_nodes_chosen)): 
			return(set_of_nodes_chosen)
			
	print("! CRITICAL ERROR: No set of nodes returned in get_set_of_node_associated_with_chosen_N_and_K. This is not normal !")
	exit(1)

def group_nodes_by_similarities(number_of_nodes, p, bandwidths, node_sizes, max_difference_allowed):
    """
    Return the mean difference in percentage between all pairs of nodes
    """
    matrix_of_differences = [[0 for i in range(number_of_nodes)] for j in range(number_of_nodes)] 
    max_difference_allowed = 0.10 # Maximum difference in percentages to consider the nodes similar
    
    for i in range (0, number_of_nodes):
        for j in range (i+1, number_of_nodes):
            reliability_diff = abs((p[i] - p[j])/float(p[i]))
            bandwidth_diff = abs((bandwidths[i] - bandwidths[j])/float(bandwidths[i]))
            size_diff = abs((node_sizes[i] - node_sizes[j])/float(node_sizes[i]))
            matrix_of_differences[i][j] = (reliability_diff + bandwidth_diff + size_diff) / 3

    return matrix_of_differences

def get_reduced_set_of_nodes(number_of_nodes, matrix_of_differences, maximum_difference_allowed):
    """
    Return a set of nodes that account for nodes similarities
    """
    set_of_nodes = list(range(0, number_of_nodes))
    reduced_set_of_nodes = []
    # deleted_nodes = 0 # This value is increased when a similarities has been found with another node in order to avoid writing out of bound
    index_in_tab = 0
    for i in (set_of_nodes):
        # index_in_tab = i - deleted_nodes
        reduced_set_of_nodes.append([])
        reduced_set_of_nodes[index_in_tab].append(i)
        for j in (set_of_nodes[i+1:]):
            # print("Compare", i, "and", j, "Similarities is", matrix_of_differences[i][j])
            if (matrix_of_differences[i][j] < maximum_difference_allowed):
                # print("Similarities!")
                reduced_set_of_nodes[index_in_tab].append(j)
                set_of_nodes.remove(j)
        index_in_tab += 1
                # deleted_nodes += 1
    return reduced_set_of_nodes
    
def update_node_sizes(set_of_nodes_chosen, K, file_size, node_sizes):
	for i in set_of_nodes_chosen:
		node_sizes[i] = node_sizes[i] - file_size/K
	return node_sizes


def exponential_function(x, x1, y1, x2, y2):
    """
    x is the free memory on the node
    Example usage of exponential for algorithm 4
	x1 = 100 # max node
	y1 = 1
	x2 = 10 # min data
	y2 = 1/number_of_nodes
	x = 11  # Remaining data after adding chunk
	result = exponential_function(x, x1, y1, x2, y2)
	print(f"f({x}) = {result}")

	By hand it is:
	f(x) = ab^x
	ab^100 = 1 -> a = b^-100 -> a = 0.077459322
	ab^10 = 0.1 ->  b^-100*b^10 = 0.1 -> b^-90 = 0.1 -> b = 1.02591
    """
    # Ensure x1 is not equal to x2
    if x1 == x2:
        raise ValueError("x1 cannot be equal to x2 in exponential_function")
    
    # Calculate the exponent
    exponent = (x - x1) / (x2 - x1)

    # Calculate the y value
    y = y1 * math.pow(y2 / y1, exponent)
    
    return y

def system_saturation(node_sizes, min_data_size, total_node_size):
	"""
	Return the system saturation between 0 and 1 using and exponential
	The closer to 1 the worst
	"""
	
	number_of_nodes = len(node_sizes)
	saturation = 0
	total_remaining_size = 0
	
	for i in range(0, number_of_nodes):
		total_remaining_size += node_sizes[i]

	saturation = 1 - exponential_function(total_remaining_size, total_node_size, 1, min_data_size, 1/number_of_nodes)

	return saturation

def nodes_can_fit_new_data(set_of_nodes_chosen, node_sizes, size_to_remove):
	"""
	Return True if the node can fit the data without getting under a memory of 0
	Else return False
	"""
	
	for i in set_of_nodes_chosen:
		if (node_sizes[i] - size_to_remove < 0):
			return False
	
	return True
