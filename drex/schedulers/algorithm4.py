from drex.utils.tool_functions import *
import time
import sys
import numpy


def algorithm4(
    number_of_nodes, 
    reliability_of_nodes, 
    bandwidths, 
    reliability_threshold, 
    file_size, real_records, 
    node_sizes, 
    max_node_size, 
    min_data_size, 
    system_saturation, 
    total_node_size,
    predictor):

    start = time.time()

    min_K = 0
    set_of_nodes_chosen = []
    set_of_nodes = list(range(0, number_of_nodes))
    set_of_possible_solutions = []
    # First value is time, then total space, then space score.
    time_space_and_size_score_from_set_of_possible_solution = []
    system_saturation = system_saturation(
        node_sizes, min_data_size, total_node_size)
    # ~ print("Saturation of the system is", system_saturation)

    # 1. Get set of N, K and associated nodes that match the reliability and put them in a list, with fastest N when multiple set of nodes can satisfy the reliability
    for i in range(2, number_of_nodes + 1):
        min_time = sys.maxsize
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
                # Getting the size score of each node and also checking we are not overflowing the nodes
                size_score = 0
                set_of_node_valid = True
                for l in set_of_nodes_chosen:
                    if (node_sizes[l] - (file_size/K) <= 0):
                        set_of_node_valid = False
                        break
                    # The lower the better. TODO future work: add time the data is spending on the system
                    size_score += 1 - exponential_function(node_sizes[l] - (
                        file_size/K), max_node_size, 1, min_data_size, 1/number_of_nodes)

                if (set_of_node_valid == True):
                    # Take the mean score over all nodes chosen
                    size_score = size_score/len(set_of_nodes_chosen)
                    # Adding them in the tuple used for pareto front
                    #replication_and_write_time = replication_and_chuncking_time(
                    #    i, K, file_size, bandwidth_of_nodes_chosen, real_records)
                    replication_and_write_time = predictor.predict(file_size, i, K, bandwidth_of_nodes_chosen)
                    set_of_possible_solutions.append(
                        (i, K, set_of_nodes_chosen, replication_and_write_time, (file_size/K)*i))
                    time_space_and_size_score_from_set_of_possible_solution.append(
                        [replication_and_write_time, (file_size/K)*i, size_score])

    if (len(time_space_and_size_score_from_set_of_possible_solution) == 0):
        print("ERROR: Algorithm 4 could not find a solution that would not overflow the memory of the nodes")
        exit(1)

    # 2. Take those that are on the 3D pareto front
    costs = numpy.asarray(
        time_space_and_size_score_from_set_of_possible_solution)
    set_of_solution_on_pareto = is_pareto_efficient(costs, False)
    # ~ print("Set on pareto front is", set_of_solution_on_pareto)

    # Just printing
    # ~ for i in set_of_solution_on_pareto:
    # ~ print(i, ":", time_space_and_size_score_from_set_of_possible_solution[i], "with nodes", set_of_possible_solutions[i][2])

    # Get min and max of each of our 3 parameters
    # set_of_solution_on_pareto[i]][0] is time, [1] is space and [2] is space score
    # For the space one is already sorted logically so don't need to use the min and max function
    # It is already sorted because the space decreases with N that increases
    # However time and score are not sorted
    size = len(set_of_solution_on_pareto) - 1
    min_space = time_space_and_size_score_from_set_of_possible_solution[
        set_of_solution_on_pareto[size]][1]
    max_space = time_space_and_size_score_from_set_of_possible_solution[
        set_of_solution_on_pareto[0]][1]
    space_score_on_pareto = []
    time_on_pareto = []
    for i in range(0, len(set_of_solution_on_pareto)):
        time_on_pareto.append(
            time_space_and_size_score_from_set_of_possible_solution[set_of_solution_on_pareto[i]][0])
        space_score_on_pareto.append(
            time_space_and_size_score_from_set_of_possible_solution[set_of_solution_on_pareto[i]][2])
    min_time = min(time_on_pareto)
    max_time = max(time_on_pareto)
    min_space_score = min(space_score_on_pareto)
    max_space_score = max(space_score_on_pareto)

    # ~ print("min_time:", min_time)
    # ~ print(max_time)
    # ~ print(min_space)
    # ~ print(max_space)
    # ~ print(min_space_score)
    # ~ print("max_space_score:", max_space_score)

    # 3. Compute score with % progress TODO progress value fix this value as they can be 0
    total_progress_time = max_time - min_time
    total_progress_space = max_space - min_space
    total_progress_space_score = max_space_score - min_space_score

    max_score = -1
    best_index = -1
    for i in range(0, size+1):
        both_space_score = 0
        time_score = 0

        if (total_progress_time > 0):  # In some cases, when there are not enough solution or if they are similar the total progress is 0. As we don't want to divide by 0, we keep the score at 0 for the corresponding value as no progress could be made
            time_score = 100 - \
                ((time_on_pareto[i] - min_time)*100)/total_progress_time
            # ~ print(set_of_solution_on_pareto[i], "made", time_score, "progress on time")

        if (total_progress_space > 0):
            both_space_score += 100 - \
                ((time_space_and_size_score_from_set_of_possible_solution[
                 set_of_solution_on_pareto[i]][1] - min_space)*100)/total_progress_space
            # ~ print(set_of_solution_on_pareto[i], "made", 100 - ((time_space_and_size_score_from_set_of_possible_solution[set_of_solution_on_pareto[i]][1] - min_space)*100)/total_progress_space, "progress on space")

        if (total_progress_space_score > 0):
            both_space_score += 100 - \
                ((space_score_on_pareto[i] - min_space_score)
                 * 100)/total_progress_space_score
            # ~ print(set_of_solution_on_pareto[i], "made", 100 - ((space_score_on_pareto[i] - min_space_score)*100)/total_progress_space_score, "progress on space score")

        # Weight with system saturation
        total_score = time_score + (both_space_score/2)*system_saturation

        if (max_score < total_score):  # Higher score the better
            max_score = total_score
            best_index = i

    min_N = set_of_possible_solutions[set_of_solution_on_pareto[best_index]][0]
    min_K = set_of_possible_solutions[set_of_solution_on_pareto[best_index]][1]
    min_set_of_nodes_chosen = set_of_possible_solutions[set_of_solution_on_pareto[best_index]][2]

    node_sizes = update_node_sizes(
        min_set_of_nodes_chosen, min_K, file_size, node_sizes)

    end = time.time()

    print("\nAlgorithm 4 chose N =", min_N, "and K =", min_K, "with the set of nodes:",
          min_set_of_nodes_chosen, "It took", end - start, "seconds.")

    return list(min_set_of_nodes_chosen), min_N, min_K, node_sizes
