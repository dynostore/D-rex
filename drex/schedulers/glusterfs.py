from drex.utils.tool_functions import *
import time

def glusterfs(N, K, number_of_nodes, reliability_of_nodes, bandwidths, reliability_threshold, file_size, node_sizes):
    """
    Uses a set N and K and ida.splyt_bytes for chunking
    """
    
    start = time.time()
	    
    if (N > number_of_nodes):
        # ~ print("glusterfs could not find a solution because N provided > number of nodes.")
        return -1, -1, -1, node_sizes
    
    size_to_stores = [file_size/K] * N

    set_of_nodes = list(range(0, number_of_nodes))
    
    # Combine nodes and bandwidths into tuples
    combined = list(zip(set_of_nodes, bandwidths))

    # Sort the combined list of tuples by bandwidth
    sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True) # Sort by the second element (bandwidth)

    # Unpack the sorted tuples into separate lists
    sorted_nodes_by_sorted_bandwidths, sorted_bandwidths = zip(*sorted_combined)

    set_of_nodes_chosen = list(sorted_nodes_by_sorted_bandwidths[:N])

    # Check if the data would fit. If not look for another node that can fit the data
    j = 0
    for i in set_of_nodes_chosen:
        if (node_sizes[i] - size_to_stores[j] < 0):
            replace_ok = False
            # Need to find a new node
            for k in set_of_nodes:
                if k not in set_of_nodes_chosen:
                    if node_sizes[k] - size_to_stores[j] >= 0:
                        set_of_nodes_chosen[j] = set_of_nodes[k]
                        replace_ok = True
                        break
            if replace_ok == False:
                return -1, -1, -1, node_sizes
        j += 1
    
    set_of_nodes_chosen = sorted(set_of_nodes_chosen)
    
    # Need to do this after the potential switch of nodes of course
    reliability_of_nodes_chosen = [reliability_of_nodes[node] for node in set_of_nodes_chosen]
    
    # Check if the reliability threshold is met. Else replace the worst node in terms of reliability with
    # the best one that is not yet in the set of nodes chosen. The same code is copy and pasted and used in
    # hdfs_three_replications
    loop = 0
    while reliability_thresold_met(N, K, reliability_threshold, reliability_of_nodes_chosen) == False:
        if (loop > number_of_nodes - N):
            # ~ print(f"gluster could not find a solution because reliability not met. (loop: {loop}, number nodes {number_of_nodes}), N: {N}")
            return -1, -1, -1, node_sizes
        
        # Find the index of the lowest reliability value
        index = 0
        index_min_reliability = 0
        min_reliability = -1
        for i in reliability_of_nodes_chosen:
            if min_reliability < i:
                min_reliability = i
                index_min_reliability = index
            index += 1
                
        # Find the index of the highest new reliability value that is not already being used
        index = 0
        index_max_reliability = 0
        max_reliability = 2
        for i in reliability_of_nodes:
            if max_reliability > i and set_of_nodes[index] not in set_of_nodes_chosen:
                max_reliability = i
                index_max_reliability = index
            index += 1
        
        # Replace the lowest reliability value with the corresponding value from reliability_of_nodes
        reliability_of_nodes_chosen[index_min_reliability] = max_reliability
        
        # Update the corresponding node in set_of_nodes_chosen
        set_of_nodes_chosen[index_min_reliability] = set_of_nodes[index_max_reliability]
        loop += 1
                
    # Custom code for update node size cause we have inconsistent data sizes
    j = 0
    for i in set_of_nodes_chosen:
        node_sizes[i] = node_sizes[i] - size_to_stores[j]
        j += 1
    
    end = time.time()
		    
    # ~ print("\nGlusterfs (Redhat) N", N, "K", K, "chose the set of nodes:", set_of_nodes_chosen, "and will remove the corresponding size from these nodes:", size_to_stores, "It took", end - start, "seconds.")
    return set_of_nodes_chosen, N, K, node_sizes
