from drex.utils.tool_functions import *
import time

def hdfs_three_replications(number_of_nodes, reliability_threshold, reliability_of_nodes, node_sizes, file_size, bandwidths, mode):
    """
    Cut the data in blocks of 128MB max and then replicate all the chunks three times.
    Choses the fastest nodes first.
    """
	
    start = time.time()
	
    # Cut data in blocks of 128MB maximum
    chunk_size = 128
    num_full_chunks = int(file_size // chunk_size) # Cast to integer in case the size is a float
    last_chunk_size = file_size % chunk_size
    # If the last chunk size is greater than 0, it means there's a partial chunk
    if last_chunk_size > 0:
        num_chunks = num_full_chunks + 1
    else:
        num_chunks = num_full_chunks
        
    N = num_chunks*3 # Times 3 because everything is replicated three times
    K = 1
    
    size_to_stores = [128] * num_full_chunks * 3 + [last_chunk_size] * 3
    
    if (N > number_of_nodes):
        print(f"ERROR: hdfs_three_replications could not find a solution (N: {N}, number nodes {number_of_nodes}).")
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
                print(f"ERROR: hdfs_three_replications could not find a solution. (k: {k}, number nodes {number_of_nodes})")
                exit(1)
        j += 1
    
    # ~ print("set_of_nodes_chosen after mem check", set_of_nodes_chosen)
    set_of_nodes_chosen = sorted(set_of_nodes_chosen)
    # ~ print("set_of_nodes_chosen after sort", set_of_nodes_chosen)

    # Need to do this after the potnetial switch of nodes of course
    reliability_of_nodes_chosen = [reliability_of_nodes[node] for node in set_of_nodes_chosen]
    
    # Check if the reliability threshold is met. Else replace the worst node in terms of reliability with
    # the best one that is not yet in the set of nodes chosen. The same code is copy and pasted and used in
    # hdfs_reed_solomon
    loop = 0
    while reliability_thresold_met(N, 1, reliability_threshold, reliability_of_nodes_chosen) == False:
        if (loop > number_of_nodes - N):
            print(f"ERROR: hdfs_three_replications could not find a solution. (loop: {loop}, number nodes {number_of_nodes}), N: {N}")
            exit(1)
        
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
	
    if mode == "simulation":
        print("\nHDFS 3 replications simulation chose N =", N, "and K =", K, "with the set of nodes:", set_of_nodes_chosen, "It took", end - start, "seconds.")
        return set_of_nodes_chosen, N, K, node_sizes
    elif mode == "real":
        print("\nHDFS 3 replications real chose the set of nodes:", set_of_nodes_chosen, "and will remove the coprresponding size from these nodes:", size_to_stores, "It took", end - start, "seconds.")
        return set_of_nodes_chosen, node_sizes, size_to_stores
    else: 
        print("Wrong mode passed to hdfs 3 replications. It must be \"simulation\" or \"real\"")
        exit(1)
    
def hdfs_reed_solomon(number_of_nodes, reliability_threshold, reliability_of_nodes, node_sizes, file_size, bandwidths, RS1, RS2):
    """
    Uses reed solomon and the fastest nodes first
    N = RS2 and to get K need to do file_size/(((1/(RS1/(RS1+RS2)))*100)/RS2)
    """
    
    start = time.time()
	
    K = file_size/(((1/(RS1/(RS1+RS2)))*file_size)/RS2)
    N = RS2
    # ~ print("With file_size:", file_size, "and RS1 (", RS1, ",", RS2, ") we have N =", N, "and K =", K, "and total size stored is thus", (file_size/K)*N)
    
    if (N > number_of_nodes):
        print("ERROR: hdfs_reed_solomon could not find a solution.")
        exit(1)
    
    size_to_stores = [file_size/K] * N

    set_of_nodes = list(range(0, number_of_nodes))
    
    # Combine nodes and bandwidths into tuples
    combined = list(zip(set_of_nodes, bandwidths))

    # Sort the combined list of tuples by bandwidth
    sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)  # Sort by the second element (bandwidth)

    # Unpack the sorted tuples into separate lists
    sorted_nodes_by_sorted_bandwidths, sorted_bandwidths = zip(*sorted_combined)

    set_of_nodes_chosen = list(sorted_nodes_by_sorted_bandwidths[:N])

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
    
    set_of_nodes_chosen = sorted(set_of_nodes_chosen)
    # ~ print(set_of_nodes_chosen)
    
    # Need to do this after the potential switch of nodes of course
    reliability_of_nodes_chosen = [reliability_of_nodes[node] for node in set_of_nodes_chosen]
    
    # Check if the reliability threshold is met. Else replace the worst node in terms of reliability with
    # the best one that is not yet in the set of nodes chosen. The same code is copy and pasted and used in
    # hdfs_three_replications
    loop = 0
    while reliability_thresold_met(N, 1, reliability_threshold, reliability_of_nodes_chosen) == False:
        if (loop > number_of_nodes - N):
            print(f"ERROR: hdfs_three_replications could not find a solution. (loop: {loop}, number nodes {number_of_nodes}), N: {N}")
            exit(1)
        
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
		    
    # ~ if mode == "simulation":
        # ~ print("\nHDFS Reed Solomon (", RS1, ",", RS2, ") simulation chose N =", N, "and K =", K, "with the set of nodes:", set_of_nodes_chosen, "It took", end - start, "seconds.")
        # ~ return set_of_nodes_chosen, N, K, node_sizes
    # ~ elif mode == "real":
    print("\nHDFS Reed Solomon (", RS1, ",", RS2, ") real chose the set of nodes:", set_of_nodes_chosen, "and will remove the corresponding size from these nodes:", size_to_stores, "It took", end - start, "seconds.")
    return set_of_nodes_chosen, N, K, node_sizes, size_to_stores
    # ~ else: 
        # ~ print("Wrong mode passed to HDFS Reed Solomon (", RS1, ",", RS2, "). It must be \"simulation\" or \"real\"")
        # ~ exit(1)
