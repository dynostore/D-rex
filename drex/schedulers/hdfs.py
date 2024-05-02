from drex.utils.tool_functions import *
import time

def hdfs_three_replications(number_of_nodes, reliability_threshold, reliability_of_nodes, node_sizes, file_size, bandwidths):
    """
    Cut the data in blocks of 128MB max and then replicate all the chunks three times.
    Choses the fastest nodes first.
    """
	
    start = time.time()
	
    # 1. Cut data in blocks of 128MB maximum
    chunk_size = 128
    num_full_chunks = file_size // chunk_size
    last_chunk_size = file_size % chunk_size
    # If the last chunk size is greater than 0, it means there's a partial chunk
    if last_chunk_size > 0:
        num_chunks = num_full_chunks + 1
    else:
        num_chunks = num_full_chunks
        
    N = num_chunks*3 # Times 3 because everything is replicated three times
    K = 1
    
    size_to_stores = [128] * num_full_chunks * 3 + [last_chunk_size] * 3
    # ~ print("size_to_stores:", size_to_stores)
    # ~ print("node_sizes:", node_sizes)
    
    if (N > number_of_nodes):
        print("ERROR: hdfs_three_replications could not find a solution.")
        exit(1)
    
    set_of_nodes = list(range(0, number_of_nodes))
    
    # Combine nodes and bandwidths into tuples
    combined = list(zip(set_of_nodes, bandwidths))

    # Sort the combined list of tuples by bandwidth
    sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)  # Sort by the second element (bandwidth)

    # Unpack the sorted tuples into separate lists
    sorted_nodes_by_sorted_bandwidths, sorted_bandwidths = zip(*sorted_combined)

    # Print the sorted lists
    # ~ print("Sorted Nodes:", sorted_nodes_by_sorted_bandwidths)
    # ~ print("Sorted Bandwidths:", sorted_bandwidths)
    # ~ print("reliability_of_nodes:", reliability_of_nodes)

    set_of_nodes_chosen = list(sorted_nodes_by_sorted_bandwidths[:N])
    # ~ print("set_of_nodes_chosen", set_of_nodes_chosen)

    # Check if the data would fit. If not look for another node that can fit the data
    j = 0
    for i in set_of_nodes_chosen:
        if (node_sizes[i] - size_to_stores[j] < 0):
            # ~ print(i, "doesn't have enough memory left")
            # Need to find a new node
            for k in set_of_nodes:
                if k not in set_of_nodes_chosen:
                    # ~ print("Trying node", k)
                    if node_sizes[k] - size_to_stores[j] >= 0:
                        set_of_nodes_chosen[j] = set_of_nodes[k]
                        break
            if k == number_of_nodes - 1:
                print("ERROR: hdfs_three_replications could not find a solution.")
                exit(1)
        j += 1
    
    # ~ print("set_of_nodes_chosen after mem check", set_of_nodes_chosen)
    set_of_nodes_chosen = sorted(set_of_nodes_chosen)
    # ~ print("set_of_nodes_chosen after sort", set_of_nodes_chosen)

    # Need to do this after the potnetial switch of nodes of course
    reliability_of_nodes_chosen = [reliability_of_nodes[node] for node in set_of_nodes_chosen]
    
    # Loop until the sum meets the threshold
    loop = 0
    # ~ print("R chosen before:", reliability_of_nodes_chosen)
    while reliability_thresold_met(N, 1, reliability_threshold, reliability_of_nodes_chosen) == False:
        # ~ print("Reliability issue")
        if (loop > number_of_nodes - N):
            print("ERROR: hdfs_three_replications could not find a solution.")
            exit(1)
        # Find the index of the lowest reliability value
        min_reliability_index = reliability_of_nodes_chosen.index(max(reliability_of_nodes_chosen))
        
        # Find the index of the highest new reliability value
        highest_new_reliability = min(filter(lambda x: x not in reliability_of_nodes_chosen, reliability_of_nodes))
        highest_new_reliability_index = reliability_of_nodes.index(highest_new_reliability)
        
        # Replace the lowest reliability value with the corresponding value from reliability_of_nodes
        reliability_of_nodes_chosen[min_reliability_index] = highest_new_reliability
        
        # Update the corresponding node in set_of_nodes_chosen
        set_of_nodes_chosen[min_reliability_index] = highest_new_reliability_index
        loop += 1
        
    # Custom code for update node size cause we have inconsistent data sizes
    j = 0
    for i in set_of_nodes_chosen:
        node_sizes[i] = node_sizes[i] - size_to_stores[j]
        j += 1
    
    end = time.time()
	
    print("\nHDFS 3 replications chose N =", N, "and K =", K, "with the set of nodes:", set_of_nodes_chosen, "It took", end - start, "seconds.")
	
    return set_of_nodes_chosen, N, K, node_sizes
    
def hdfs_reed_solomon(number_of_nodes, reliability_threshold, reliability_of_nodes, node_sizes, file_size, bandwidths, RS1, RS2):
    """
    Uses reed solomon and the fastest nodes first
    """
	
    start = time.time()
	        
    N = RS2 # N is equal at the parity number
    K = RS1/RS2 # K is the number of data block per parity block
    
    if (N > number_of_nodes):
        print("ERROR: hdfs_reed_solomon could not find a solution.")
        exit(1)
    
    set_of_nodes = list(range(0, number_of_nodes))
    
    # Combine nodes and bandwidths into tuples
    combined = list(zip(set_of_nodes, bandwidths))

    # Sort the combined list of tuples by bandwidth
    sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)  # Sort by the second element (bandwidth)

    # Unpack the sorted tuples into separate lists
    sorted_nodes_by_sorted_bandwidths, sorted_bandwidths = zip(*sorted_combined)

    set_of_nodes_chosen = list(sorted_nodes_by_sorted_bandwidths[:N])

    # Checking if the data would fit, if not replace some of the nodes
    added_switch = 0
    j = 0
    for i in set_of_nodes_chosen:
        if (node_sizes[i] - file_size/K < 0):
			# Need to find a new node
            if (N + added_switch > number_of_nodes):
                print("ERROR: hdfs_reed_solomon could not find a solution.")
                exit(1)
            set_of_nodes_chosen[j] = sorted_nodes_by_sorted_bandwidths[N + added_switch]
            added_switch += 1
        j += 1
    
    set_of_nodes_chosen = sorted(set_of_nodes_chosen)
    # ~ print(set_of_nodes_chosen)
    
    # Need to do this after the potnetial switch of nodes of course
    reliability_of_nodes_chosen = [reliability_of_nodes[node] for node in set_of_nodes_chosen]
    
    # Loop until the sum meets the threshold
    loop = 0
    # ~ print("R chosen before:", reliability_of_nodes_chosen)
    while reliability_thresold_met(N, 1, reliability_threshold, reliability_of_nodes_chosen) == False:
        # ~ print("Reliability issue")
        if (loop > number_of_nodes - N):
            print("ERROR: hdfs_three_replications could not find a solution.")
            exit(1)
        # Find the index of the lowest reliability value
        min_reliability_index = reliability_of_nodes_chosen.index(max(reliability_of_nodes_chosen))
        
        # Find the index of the highest new reliability value
        highest_new_reliability = min(filter(lambda x: x not in reliability_of_nodes_chosen, reliability_of_nodes))
        highest_new_reliability_index = reliability_of_nodes.index(highest_new_reliability)
        
        # Replace the lowest reliability value with the corresponding value from reliability_of_nodes
        reliability_of_nodes_chosen[min_reliability_index] = highest_new_reliability
        
        # Update the corresponding node in set_of_nodes_chosen
        set_of_nodes_chosen[min_reliability_index] = highest_new_reliability_index
        loop += 1
        
    # Custom code for update node size cause we have inconsistent data sizes
    j = 0
    for i in set_of_nodes_chosen:
        node_sizes[i] = node_sizes[i] - size_to_stores[j]
        j += 1
    
    end = time.time()
	
    print("\nHDFS Reed Solomon (", RS1, ",", RS2, ") chose N =", N, "and K =", K, "with the set of nodes:", set_of_nodes_chosen, "It took", end - start, "seconds.")
	
    return set_of_nodes_chosen, N, K, node_sizes
