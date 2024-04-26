from drex.utils.tool_functions import *
from drex.utils.prediction import Predictor
import sys
import time



def algorithm2(number_of_nodes, reliability_of_nodes, bandwidths, reliability_threshold, file_size, real_records, node_sizes, predictor):
    """
    Choose fastest N and biggest K
    """
    start = time.time()

    min_time = sys.maxsize
    min_N = -1
    min_K = -1
    set_of_nodes_chosen = []
    set_of_nodes = list(range(0, number_of_nodes))

    for i in range(3, number_of_nodes + 1):
        for set_of_nodes_chosen in itertools.combinations(set_of_nodes, i):
            reliability_of_nodes_chosen = []
            bandwidth_of_nodes_chosen = []
            for j in range(0, len(set_of_nodes_chosen)):
                reliability_of_nodes_chosen.append(
                    reliability_of_nodes[set_of_nodes_chosen[j]])
                bandwidth_of_nodes_chosen.append(
                    bandwidths[set_of_nodes_chosen[j]])
            K = get_max_K_from_reliability_threshold_and_nodes_chosen(
                i, reliability_threshold, reliability_of_nodes_chosen)
            if (K != -1):
                #replication_and_write_time = replication_and_chuncking_time(i, K, file_size, bandwidth_of_nodes_chosen, real_records)
                replication_and_write_time = predictor.predict(file_size, i, K, bandwidth_of_nodes_chosen)
                
                if (replication_and_write_time < min_time and nodes_can_fit_new_data(set_of_nodes_chosen, node_sizes, file_size/K)):
                    min_time = replication_and_write_time
                    min_N = i
                    min_K = K
                    min_set_of_nodes_chosen = set_of_nodes_chosen

    if (min_K == -1):
        print("ERROR: Algorithm 2 could not find a solution that would not overflow the memory of the nodes")
        exit(1)

    node_sizes = update_node_sizes(
        min_set_of_nodes_chosen, min_K, file_size, node_sizes)

    end = time.time()

    print("\nAlgorithm 2 chose N =", min_N, "and K =", min_K, "with the set of nodes:",
          min_set_of_nodes_chosen, "It took", end - start, "seconds.")

    return list(min_set_of_nodes_chosen), min_N, min_K, node_sizes


def algorithm2_reduced_complexity(number_of_nodes, reliability_of_nodes, bandwidths, reliability_threshold, file_size, real_records, node_sizes, reduced_set_of_nodes, iteration, maximum_difference_allowed):
    """
    DOES NOT WORK BECAUSE DOES NOT CONSIDER ALL SET OF NODES CORRECTLY BECAUSE OF THE SIMPLIFICATION
    Choose fastest N and biggest K.
    Uses a set of node simplified where we only check the first node of the pack.
    Means we have to loop through the simplified node pack when we have a memory constraint to use the next nodes.
    """

    start = time.time()
    print(node_sizes)
    if (iteration == 0):
        # For reduced complexity we need to call this function that groups similar nodes together and get the reduced set of nodes
        matrix_of_differences = group_nodes_by_similarities(
            number_of_nodes, reliability_of_nodes, bandwidths, node_sizes, maximum_difference_allowed)
        reduced_set_of_nodes = get_reduced_set_of_nodes(
            number_of_nodes, matrix_of_differences, maximum_difference_allowed)
        print("reduced_set_of_nodes:", reduced_set_of_nodes)

    iteration += 1
    min_time = sys.maxsize
    min_N = -1
    min_K = -1
    set_of_nodes_chosen = []
    # The set of nodes only get the first of each subset of similar nodes
    set_of_nodes = [sub_array[0] for sub_array in reduced_set_of_nodes]
    print("set_of_nodes:", set_of_nodes)
    set_of_nodes_corresponding_index_in_reduced_set_of_nodes = list(
        range(0, number_of_nodes))
    index = 0
    for i in reduced_set_of_nodes:
        for j in i:
            set_of_nodes_corresponding_index_in_reduced_set_of_nodes[j] = index
        index += 1
    print(set_of_nodes_corresponding_index_in_reduced_set_of_nodes)

    for i in range(3, number_of_nodes + 1):
        for set_of_nodes_chosen in itertools.combinations(set_of_nodes, i):
            set_of_nodes_chosen = list(set_of_nodes_chosen)
            print("Testing", set_of_nodes_chosen)
            reliability_of_nodes_chosen = []
            bandwidth_of_nodes_chosen = []
            for j in range(0, len(set_of_nodes_chosen)):
                reliability_of_nodes_chosen.append(
                    reliability_of_nodes[set_of_nodes_chosen[j]])
                bandwidth_of_nodes_chosen.append(
                    bandwidths[set_of_nodes_chosen[j]])
            K = get_max_K_from_reliability_threshold_and_nodes_chosen(
                i, reliability_threshold, reliability_of_nodes_chosen)
            if (K != -1):
                #replication_and_write_time = replication_and_chuncking_time(
                #    i, K, file_size, bandwidth_of_nodes_chosen, real_records)
                replication_and_write_time = predictor.predict(file_size, i, K, bandwidth_of_nodes_chosen)
                if (replication_and_write_time < min_time):
                    fit_on_nodes = True
                    print("Checking set_of_nodes_chosen", set_of_nodes_chosen)
                    node_index = 0
                    node_ok = False
                    for node in set_of_nodes_chosen:
                        if (node_sizes[node] - file_size/K < 0):
                            node_ok = False
                            print("Would not fit on node", node, "memory only",
                                  node_sizes[node], "index", set_of_nodes_corresponding_index_in_reduced_set_of_nodes[node], "in reduced set of nodes")
                            print("Check next reduced_set_of_nodes:", reduced_set_of_nodes, "avail len is", len(
                                reduced_set_of_nodes[set_of_nodes_corresponding_index_in_reduced_set_of_nodes[node]]))
                            for l in range(1, len(reduced_set_of_nodes[set_of_nodes_corresponding_index_in_reduced_set_of_nodes[node]])):
                                next_possible_node = reduced_set_of_nodes[
                                    set_of_nodes_corresponding_index_in_reduced_set_of_nodes[node]][l]
                                print("Checking next possible node:",
                                      next_possible_node)
                                # If it would fit, use it
                                if (node_sizes[next_possible_node] - file_size/K >= 0):
                                    set_of_nodes_chosen[node_index] = next_possible_node
                                    reliability_of_nodes_chosen[node_index] = reliability_of_nodes[next_possible_node]
                                    print("Switch ok with new node",
                                          next_possible_node)
                                    node_ok = True
                                    break
                            if node_ok == False:
                                fit_on_nodes = False
                                break
                        node_index += 1
                    if node_ok == True:  # There has been a switch
                        print("New set of nodes after switch is",
                              set_of_nodes_chosen)
                        if reliability_thresold_met(len(set_of_nodes_chosen), K, reliability_threshold, reliability_of_nodes_chosen) == False:
                            fit_on_nodes = False
                    if (fit_on_nodes == True):
                        min_time = replication_and_write_time
                        min_N = i
                        min_K = K
                        min_set_of_nodes_chosen = set_of_nodes_chosen

    if (min_K == -1):
        print("ERROR: Algorithm 2 reduced complexity could not find a solution that would not overflow the memory of the nodes")
        exit(1)

    node_sizes = update_node_sizes(
        min_set_of_nodes_chosen, min_K, file_size, node_sizes)

    end = time.time()

    print("\nAlgorithm 2 with reduced complexity chose N =", min_N, "and K =", min_K,
          "with the set of nodes:", min_set_of_nodes_chosen, "It took", end - start, "seconds.")

    return list(min_set_of_nodes_chosen), min_N, min_K, node_sizes, iteration, reduced_set_of_nodes
