from drex.utils.tool_functions import *
import time

def hdfs_three_replications(number_of_nodes, reliability_threshold, reliability_of_nodes, node_sizes, file_size, bandwidths, mode):
    """
    Cut the data in blocks of 128MB max and then replicate all the blocks three times.
    Choses the fastest nodes first.
    When a node is full, uses the remaining nodes while the reiability is matched.
    First cut in pieces of 128 MB.
    Each piece must be on three different nodes but no need to necessarly put all of them on the same 3 nodes if one of them is full.
    Thus, we first take the 3 fastest nodes if the reliability match.
    """
    
    # ~ print("Start 3 rep")
    # ~ print("Node sizes:", node_sizes)
    # ~ print("bandwidths:", bandwidths)
    
    start = time.time()
	
    # ~ # Total size we need to store
    # ~ total_size_to_store = file_size*3
        
    # ~ # Cut data in blocks of 128MB maximum
    # ~ chunk_size = 128
    # ~ num_full_chunks = int(total_size_to_store // chunk_size) # Cast to integer in case the size is a float
    # ~ last_chunk_size = total_size_to_store % chunk_size
    # ~ # If the last chunk size is greater than 0, it means there's a partial chunk
    # ~ if last_chunk_size > 0:
        # ~ num_chunks = num_full_chunks + 1
    # ~ else:
        # ~ num_chunks = num_full_chunks
    
    # Sort nodes by bandwidth
    set_of_nodes = list(range(0, number_of_nodes))
    
    # Filter out nodes with less than 128 MB
    filtered_nodes = [node for node, size in zip(set_of_nodes, node_sizes) if size < float('inf') and size >= 128]
    
    set_of_nodes = filtered_nodes
    # ~ print("set_of_nodes after 128MB filter:", set_of_nodes)
    
    # Combine nodes and bandwidths into tuples
    combined = list(zip(set_of_nodes, bandwidths))
    # Sort the combined list of tuples by bandwidth
    sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)  # Sort by the second element (bandwidth)
    # Unpack the sorted tuples into separate lists
    sorted_nodes_by_sorted_bandwidths, sorted_bandwidths = zip(*sorted_combined)
    set_of_nodes_chosen = list(sorted_nodes_by_sorted_bandwidths[:3])
    
    if (len(set_of_nodes_chosen) < 3):
        # ~ print("Not enough memory left to fit the data")
        return -1, -1, -1, node_sizes
    
    # ~ print("Initial fastest nodes chosen:", set_of_nodes_chosen)
    
    # ~ # Need to do this after the potential switch of nodes of course
    reliability_of_nodes_chosen = [reliability_of_nodes[node] for node in set_of_nodes_chosen]
    
    # Check if the reliability threshold is met. Else replace the worst node in terms of reliability with
    # the best one that is not yet in the set of nodes chosen. The same code is copy and pasted and used in
    # hdfs_reed_solomon
    loop = 0
    while reliability_thresold_met(3, 1, reliability_threshold, reliability_of_nodes_chosen) == False:
        # ~ print("Need new nodes because reliability doesn't match")
        if (loop > number_of_nodes - 3):
            # ~ print(f"ERROR: hdfs_three_replications could not find a solution. (loop: {loop}, number nodes {number_of_nodes}), N: {N}")
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
        # ~ print("Reliability doesn't match, replace with", index_max_reliability)
        loop += 1
    
    # Start filling with data the 3 nodes
    size_to_stores = []
    rest_to_store = 0
    N = 3
    K = 1
    for i in set_of_nodes_chosen:
        if file_size <= node_sizes[i]: # all fit
            # ~ node_sizes[i] = node_sizes[i] - file_size
            size_to_stores.append(file_size)
        # ~ elif node_sizes[i] < 128:
            # ~ rest_to_store += file_size
            # ~ size_to_stores.append(
        else: # all doesn't fit so put as much as possible and we'll put the rest on another node
            rest_to_store += file_size - node_sizes[i]
            # ~ node_sizes[i] = 0
            size_to_stores.append(node_sizes[i])
    # ~ print("size_to_stores:", size_to_stores)
    # ~ print("rest_to_store:", rest_to_store)
    if rest_to_store != 0: # We have left overs to put on a fourth node or more
        all_good = False
        for i in set_of_nodes:
            if i not in set_of_nodes_chosen:
                set_of_nodes_chosen.append(i)
                reliability_of_nodes_chosen = [reliability_of_nodes[node] for node in set_of_nodes_chosen]
                N += 1
                K += 1
                # ~ print("Try", set_of_nodes_chosen, reliability_of_nodes_chosen, N, K)
                if reliability_thresold_met(N, K, reliability_threshold, reliability_of_nodes_chosen) == True:
                    if rest_to_store <= node_sizes[i]:
                        # ~ node_sizes[i] = node_sizes[i] - file_size
                        size_to_stores.append(rest_to_store)
                        all_good = True
                        break
                    else: # Need again another node
                        rest_to_store -= node_sizes[i]
                        # ~ node_sizes[i] = 0
                        size_to_stores.append(node_sizes[i])
                else:
                    # ~ print("False")
                    K -= 1
                    N -= 1
                    set_of_nodes_chosen.remove(i)
        if all_good == False:
            # Need to loop and find a solution that works in terms of reliability
            for set_of_nodes_chosen in itertools.combinations(set_of_nodes, 3):
                # ~ print("After everything failed, try", set_of_nodes_chosen)
                reliability_of_nodes_chosen = [reliability_of_nodes[node] for node in set_of_nodes_chosen]
                if reliability_thresold_met(3, 1, reliability_threshold, reliability_of_nodes_chosen) == True:
                    size_to_stores = []
                    all_good_2 = True
                    for i in set_of_nodes_chosen:
                        if file_size <= node_sizes[i]: # all fit
                            size_to_stores.append(file_size)
                        else:
                            all_good_2 = False
                            break
                    if all_good_2 == True:
                        # ~ print("It works!")
                        break
            if all_good_2 == False:
                # ~ print("Error size HDFS 3 replications")
                return -1, -1, -1, node_sizes
    # ~ print("size_to_stores:", size_to_stores)        
    # Custom code for update node size cause we have inconsistent data sizes
    j = 0
    for i in set_of_nodes_chosen:
        # ~ print("Remove size", size_to_stores[j], "from node", i)
        node_sizes[i] = node_sizes[i] - size_to_stores[j]
        j += 1
    
    end = time.time()
	
    if mode == "simulation":
        # ~ print("\nHDFS 3 replications simulation chose N =", N, "and K =", K, "with the set of nodes:", set_of_nodes_chosen, "It took", end - start, "seconds.")
        return set_of_nodes_chosen, N, K, node_sizes
    elif mode == "real":
        # ~ print("\nHDFS 3 replications real chose the set of nodes:", set_of_nodes_chosen, "and will remove the coprresponding size from these nodes:", size_to_stores, "It took", end - start, "seconds.")
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
	
    # ~ K = file_size/(((1/(RS1/(RS1+RS2)))*file_size)/RS2)
    # ~ K = file_size/((file_size + file_size*(50/100))/(RS1+RS2))
    K = RS1
    N = RS1 + RS2
    # ~ print("With file_size:", file_size, "and RS1 (", RS1, ",", RS2, ") we have N =", N, "and K =", K, "and total size stored is thus", (file_size/K)*N)
    
    if (N > number_of_nodes):
        # ~ print("Hdfs_reed_solomon could not find a solution.")
        return -1, -1, -1, node_sizes, -1
    
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
            # Need to find a new node
            replace_ok = False
            for k in set_of_nodes:
                if k not in set_of_nodes_chosen:
                    # ~ print("Trying node", k)
                    if node_sizes[k] - size_to_stores[j] >= 0:
                        set_of_nodes_chosen[j] = set_of_nodes[k]
                        # ~ print("Replace")
                        replace_ok = True
                        break
            if replace_ok == False:
                # ~ print("Hdfs_rs could not find a solution.")
                return -1, -1, -1, node_sizes, -1
        j += 1
    
    set_of_nodes_chosen = sorted(set_of_nodes_chosen)
    # ~ print("After:", set_of_nodes_chosen)
    
    # Need to do this after the potential switch of nodes of course
    reliability_of_nodes_chosen = [reliability_of_nodes[node] for node in set_of_nodes_chosen]
    
    # Check if the reliability threshold is met. Else replace the worst node in terms of reliability with
    # the best one that is not yet in the set of nodes chosen. The same code is copy and pasted and used in
    # hdfs_three_replications
    loop = 0
    while reliability_thresold_met(N, K, reliability_threshold, reliability_of_nodes_chosen) == False:
        if (loop > number_of_nodes - N):
            # ~ print(f"Hdfs_rs could not find a solution in term of resilience. (loop: {loop}, number nodes {number_of_nodes}), N: {N}")
            return -1, -1, -1, node_sizes, -1
        
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
    # ~ print("\nHDFS Reed Solomon (", RS1, ",", RS2, ") real chose the set of nodes:", set_of_nodes_chosen, "and will remove the corresponding size from these nodes:", size_to_stores, "It took", end - start, "seconds.")
    return set_of_nodes_chosen, N, K, node_sizes, size_to_stores
    # ~ else: 
        # ~ print("Wrong mode passed to HDFS Reed Solomon (", RS1, ",", RS2, "). It must be \"simulation\" or \"real\"")
        # ~ exit(1)
