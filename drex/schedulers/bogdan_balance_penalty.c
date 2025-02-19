#include <stdio.h>
#include <math.h>
#include <float.h>
#include <stdlib.h>
#include <stdbool.h>
#include <../schedulers/algorithm4.h>
#include <../utils/k_means_clustering.h>
#include <../schedulers/bogdan_balance_penalty.h>
#include "../utils/prediction.h"
#include <sys/time.h>

double* extract_first_X_reliabilities(Node* nodes, int total_nodes, int X) {
    // Ensure X does not exceed the total number of nodes
    if (X > total_nodes) {
        X = total_nodes;
    }

    // Allocate memory for the result array
    double* reliabilities = malloc(X * sizeof(double));
    if (reliabilities == NULL) {
        // Handle memory allocation failure
        perror("Failed to allocate memory for reliabilities");
        exit(EXIT_FAILURE);
    }

    // Extract the first X reliability values
    for (int i = 0; i < X; i++) {
        reliabilities[i] = nodes[i].probability_failure;
    }

    return reliabilities;
}

bool is_P_and_D_combination_possible (int D, int P, Node* nodes, float reliability_threshold, int number_of_nodes) {
    double* reliability_of_nodes = extract_first_X_reliabilities(nodes, number_of_nodes, D + P);
    return reliability_threshold_met_accurate(D + P, D, reliability_threshold, reliability_of_nodes);
}

double get_avg_free_storage (int number_of_nodes, Node* nodes) {
    double total_free_storage = 0;
    for (int i = 0; i < number_of_nodes; i++) {
        total_free_storage += nodes[i].storage_size;
    }
    return total_free_storage/number_of_nodes;
}

/**
for (i = 0; i < K; i++) {    
    device = sort(0..N-1 in order of free capacity)
    avg_free_capacity = sum(free_capacity[0..N-1]) / N
    min_balance_penalty = inf
    min_D = 0
    for (D = 1; D < N - P; D++) { 
        C = D + P
        chunk_size = S / D
        for (j = 0; j < C; j++) {
            if (free[device[j]] < chunk_size)
                continue;
            balance_penalty += abs(free[device[j]] - chunk_size - avg_free_capacity);
        }
        for (j = C; j < N; j++)
            balance_penalty += abs(free[device[j]] - avg_free_capacity);
        if (balance_penalty < min_balance_penalty) {
            min_D = D;
            min_balance_penalty = balance_penalty;
        }
    }
    if (min_D == 0)
        exit_with_error
    for (j = 0; j < min_D + P; j++) {
        write(chunk_j)
        free_capacity[j] -= chunk_size
    }    
}
 * D for data chunks and P for parity chunks and (D+P)*chunk_size = total_size and S for data size
 * Then you maximize D so you can minimize P * chunk_size
 * Idea that you have a penalty for nodes that need to store a chunk and a penalty for nodes that don't and you need to add all of them up to obtain the overall penalty
 **/
//~ void balance_penalty_algorithm (int number_of_nodes, Node* nodes, float reliability_threshold, double size, double max_node_size, double min_data_size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, Combination **combinations, int total_combinations, double* total_remaining_size, double total_storage_size, int closest_index, RealRecords* records_array, LinearModel* models, int nearest_size, DataList* list, int data_id) {
void balance_penalty_algorithm (int number_of_nodes, Node* nodes, float reliability_threshold, double S, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, double* total_remaining_size, int closest_index, LinearModel* models, LinearModel* models_reconstruct, int nearest_size, DataList* list, int data_id, int max_N, double* total_read_time_parrallelized, double* total_read_time, double* size_stored) {
    struct timeval start, end;
    gettimeofday(&start, NULL);
    long seconds, useconds;
    double balance_penalty;
    double min_balance_penalty = DBL_MAX;
    int D;
    int C;
    int min_D = -1;
    double chunk_size;
    *N = -1;
    *K = -1;
    int j;
    int P = 1;
    bool solution_is_not_possible;
    
    // Sorting the nodes by available memory left
    qsort(nodes, number_of_nodes, sizeof(Node), compare_nodes_by_storage_desc_with_condition);
    //~ print_nodes(nodes, number_of_nodes);
    
    // Get average free memory
    double avg_free_capacity = get_avg_free_storage(number_of_nodes, nodes); // TODO: do this when adding data to a node so we don't have to compute it for every single call of the function ?
    //~ printf("avg_free_capacity = %f\n", avg_free_capacity);

    for (P = 1; P < max_N - 1; P++) {
        if (min_D == -1) { // We only increase P if we haven't found a solution yet
            for (D = 2; D < max_N - P; D++) {
                //~ printf("P = %d, D= %d\n", P, D);
                
                if (!is_P_and_D_combination_possible(D, P, nodes, reliability_threshold, number_of_nodes)) {
                    //~ printf("Not possible for reliability, continue\n");
                    continue;
                }
                
                C = D + P;
                //~ printf("C = %d\n", C);
                balance_penalty = 0;
                chunk_size = S / D;
                //~ printf("chunk_size = %f\n", chunk_size);
                solution_is_not_possible = false;
                for (j = 0; j < C; j++) {
                    if (nodes[j].storage_size < chunk_size)
                    {
                        solution_is_not_possible = true;
                        break;
                    }
                    //~ printf("+= %f in 1st for loop\n", fabs(nodes[j].storage_size - chunk_size - avg_free_capacity));
                    balance_penalty += fabs(nodes[j].storage_size - chunk_size - avg_free_capacity);
                } 
                
                if (solution_is_not_possible == false) {
                    for (j = C; j < number_of_nodes; j++) {
                        //~ printf("+= %f in 2nd for loopc\n", fabs(nodes[j].storage_size - avg_free_capacity));
                        balance_penalty += fabs(nodes[j].storage_size - avg_free_capacity);
                    }
                    
                    if (balance_penalty < min_balance_penalty) {
                        //~ printf("New min_D %f with %d\n", min_balance_penalty, D);
                        min_D = D;
                        min_balance_penalty = balance_penalty;
                    }
                }
            }
        }
        else {
            P = P - 1; // We take the last P, the one that worked
            break;
        }
    }
    
    if (min_D != -1) { // We have a valid solution
                        
        // Update N, K, memory sizes and write results
        *N = min_D + P;
        *K = *N - P;
        
        gettimeofday(&end, NULL);
        
        double min_write_bandwidth = DBL_MAX;
        double min_read_bandwidth = DBL_MAX;
        
        // Writing down the results
        double total_upload_time_to_print = 0;
        
        /** Read **/
        double total_read_time_to_print = 0;
        double total_read_time_parralelized_to_print = 0;
        double reconstruct_time = 0;
        
        chunk_size = S/(*K);
        //~ printf("%f, %f, %d, %d, ", S, chunk_size, *N, *K);
        *number_of_data_stored += 1;
        *total_N += *N;
        *total_storage_used += chunk_size*(*N);
        *total_remaining_size -= chunk_size*(*N);
        *size_stored += S;
        
        int* used_combinations = malloc(*N * sizeof(int));
        
        for (j = 0; j < *N; j++) {
            total_upload_time_to_print += chunk_size/nodes[j].write_bandwidth;
            
            /** Read **/
            total_read_time_to_print += chunk_size/nodes[j].read_bandwidth;
                    
            nodes[j].storage_size -= chunk_size;
            //~ printf("%d ", nodes[j].id);
            if (min_write_bandwidth > nodes[j].write_bandwidth) {
                min_write_bandwidth = nodes[j].write_bandwidth;
            }
            if (min_read_bandwidth > nodes[j].read_bandwidth) {
                min_read_bandwidth = nodes[j].read_bandwidth;
            }
            
            // To track the chunks I a fill a temp struct with nodes
            used_combinations[j] = nodes[j].id;
        }
        //~ printf("\n");
        
        // Adding the chunks in the chosen nodes
        add_shared_chunks_to_nodes(used_combinations, *N, data_id, chunk_size, nodes, number_of_nodes, S);

        //~ *total_parralelized_upload_time += chunk_size/min_write_bandwidth;
        *total_parralelized_upload_time += fmax(S/out_going_bandwidth, chunk_size/min_write_bandwidth);
        
        /** Read **/
        //~ total_read_time_parralelized_to_print = chunk_size/min_read_bandwidth;
        total_read_time_parralelized_to_print = fmax(S/out_going_bandwidth, chunk_size/min_read_bandwidth);
        reconstruct_time = predict_reconstruct(models_reconstruct[closest_index], *N, *K, nearest_size, S);

        // TODO: remove this 3 lines under to reduce complexity if we don't need the trace per data
        double chunking_time = predict(models[closest_index], *N, *K, nearest_size, S);
        double transfer_time_parralelized = calculate_transfer_time(chunk_size, min_write_bandwidth);
        add_node_to_print(list, data_id, S, total_upload_time_to_print, transfer_time_parralelized, chunking_time, *N, *K, total_read_time_to_print, total_read_time_parralelized_to_print, reconstruct_time);
        
        /** Read **/
        *total_read_time_parrallelized += total_read_time_parralelized_to_print;
        *total_read_time += total_read_time_to_print;

        *total_upload_time += total_upload_time_to_print;
        
        free(used_combinations);
    }

    gettimeofday(&end, NULL);
    seconds  = end.tv_sec  - start.tv_sec;
    useconds = end.tv_usec - start.tv_usec;
    *total_scheduling_time += seconds + useconds/1000000.0;
}
