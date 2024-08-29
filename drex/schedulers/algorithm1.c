#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <stdbool.h>
#include <sys/time.h>
#include <../schedulers/algorithm4.h>
#include "../utils/prediction.h"

void min_storage(int number_of_nodes, Node* nodes, float reliability_threshold, double size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, int closest_index, LinearModel* models, int nearest_size, DataList* list, int data_id, int max_N) {
    struct timeval start, end;
    gettimeofday(&start, NULL);
    long seconds, useconds;
    *N = -1;
    *K = -1;

    // Sort indices based on bandwidth in descending order
    qsort(nodes, number_of_nodes, sizeof(Node), compare_nodes_by_storage_desc_with_condition);
    //~ print_nodes(nodes, number_of_nodes);
    int temp_N = 0;
    //~ for (temp_N = number_of_nodes; temp_N > 2; temp_N--) {
    for (temp_N = max_N; temp_N > 2; temp_N--) {
        int* set_of_nodes_chosen_temp = (int*)malloc(temp_N * sizeof(int));
        if (set_of_nodes_chosen_temp == NULL) {
            perror("Failed to allocate memory");
            exit(EXIT_FAILURE);
        }
                
        // Select the top N nodes
        for (int i = 0; i < temp_N; i++) {
            set_of_nodes_chosen_temp[i] = i;
        }
        
        double* reliability_of_nodes_chosen = (double*)malloc(temp_N * sizeof(double));
        if (reliability_of_nodes_chosen == NULL) {
            perror("Failed to allocate memory");
            exit(EXIT_FAILURE);
        }
        
        // Get reliability for the selected nodes
        for (int i = 0; i < temp_N; i++) {
            reliability_of_nodes_chosen[i] = nodes[set_of_nodes_chosen_temp[i]].probability_failure;
            //~ printf("%f\n", reliability_of_nodes_chosen[i]);
        }
        
        //~ int K = get_max_K_from_reliability_threshold_and_nodes_chosen(N, reliability_threshold, reliability_of_nodes_chosen);
        *K = get_max_K_from_reliability_threshold_and_nodes_chosen(temp_N, reliability_threshold, 0, 0, reliability_of_nodes_chosen);
        
        if (*K != -1) {
            int found = 1;
            for (int i = 0; i < temp_N; i++) {
                int node = set_of_nodes_chosen_temp[i];
                if (nodes[node].storage_size - (size / *K) < 0) {
                    found = 0;
                    //~ printf("break %f inf to %f\n", nodes[node].storage_size, (size / *K));
                    break;
                }
            }
            
            if (found) {
                *N = temp_N;
                
                double min_write_bandwidth = DBL_MAX;
                
                // Writing down the results
                double total_upload_time_to_print = 0;
                double chunk_size = size/(*K);
                *number_of_data_stored += 1;
                *total_N += *N;
                *total_storage_used += chunk_size*(*N);
                
                int* used_combinations = malloc(*N * sizeof(int));
                
                for (int j = 0; j < *N; j++) {
                    total_upload_time_to_print += chunk_size/nodes[j].write_bandwidth;
                    nodes[j].storage_size -= chunk_size;
                    if (min_write_bandwidth > nodes[j].write_bandwidth) {
                        min_write_bandwidth = nodes[j].write_bandwidth;
                    }
                    
                    // To track the chunks I a fill a temp struct with nodes
                    used_combinations[j] = nodes[j].id;
                }
                
                // Adding the chunks in the chosen nodes
                add_shared_chunks_to_nodes(used_combinations, *N, data_id, chunk_size, nodes, number_of_nodes, size);

                *total_parralelized_upload_time += chunk_size/min_write_bandwidth;
                
                // TODO: remove this 3 lines under to reduce complexity if we don't need the trace per data
                double chunking_time = predict(models[closest_index], *N, *K, nearest_size, size);
                double transfer_time_parralelized = calculate_transfer_time(chunk_size, min_write_bandwidth);
                add_node_to_print(list, data_id, size, total_upload_time_to_print, transfer_time_parralelized, chunking_time, *N, *K);

                *total_upload_time += total_upload_time_to_print;
                
                free(set_of_nodes_chosen_temp);
                free(used_combinations);
                free(reliability_of_nodes_chosen);

                gettimeofday(&end, NULL);
                seconds  = end.tv_sec  - start.tv_sec;
                useconds = end.tv_usec - start.tv_usec;
                *total_scheduling_time += seconds + useconds/1000000.0;
                return;
            }
        }
        
        free(set_of_nodes_chosen_temp);
        free(reliability_of_nodes_chosen);
    }
    
    // No valid solution found
    *N = -1;
    *K = -1;
    
    gettimeofday(&end, NULL);
    seconds  = end.tv_sec  - start.tv_sec;
    useconds = end.tv_usec - start.tv_usec;
    *total_scheduling_time += seconds + useconds/1000000.0;
}
