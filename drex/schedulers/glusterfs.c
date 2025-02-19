#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <stdbool.h>
#include <sys/time.h>
#include <../schedulers/algorithm4.h>
#include <../schedulers/random.h>
#include "../utils/prediction.h"

// Helper function to check if a value exists in an array
int in_array(int* array, int size, int value) {
    for (int i = 0; i < size; i++) {
        if (array[i] == value) {
            return 1;  // Value found
        }
    }
    return 0;  // Value not found
}

void glusterfs(int number_of_nodes, Node* nodes, float reliability_threshold, double size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, int closest_index, LinearModel* models, LinearModel* models_reconstruct, int nearest_size, DataList* list, int data_id, int RS1, int RS2, double* total_read_time_parrallelized, double* total_read_time, bool is_daos, int max_N, double* size_stored) {
    struct timeval start, end;
    gettimeofday(&start, NULL);
    long seconds, useconds;
    
    *N = RS1;
    *K = RS2;
    
    /** Daos adapt it's replication values depending on if it has more or less that 10 nodes 
     *  When RS1 == 1 we do: 
     *  RF:1
     *  domain_nr >= 10 : OC_EC_8P1GX
     *  domain_nr >= 6 : OC_EC_4P1GX
     *  When RS1 == 2 we do:
     *  RF:2
     *  domain_nr >= 10 : OC_EC_8P2GX
     *  domain_nr >= 6 : OC_EC_4P2GX
     **/
    start : ;
    if (is_daos == true) {
        //~ printf("is daos true %d nodes\n", number_of_nodes);
        if (RS1 == 3) {
            *N = 4;
            *K = 1;
        }
        else if (RS1 == 4) {
            *N = 6;
            *K = 1;
        }
        else if (number_of_nodes >= 10 && max_N > 6) {
            if (RS1 == 1) {
                *N = 9;
                *K = 8;
            }
            else if (RS1 == 2) {
                *N = 10;
                *K = 8;
            }
            //~ else { printf("Wrong RS1 value for DAOS\n"); exit(1); }
        }
        else if (number_of_nodes >= 6) {
        //~ printf("number_of_nodes sup 6\n");
           if (RS1 == 1) {
                *N = 5;
                *K = 4;
            }
            else if (RS1 == 2) {
                *N = 6;
                *K = 4;
            }
            //~ else { printf("Wrong RS1 value for DAOS\n"); exit(1); } 
        }
        else {
            *N = -1;
            *K = -1;
            gettimeofday(&end, NULL);
            seconds  = end.tv_sec  - start.tv_sec;
            useconds = end.tv_usec - start.tv_usec;
            *total_scheduling_time += seconds + useconds/1000000.0;
            return;
        }
        //~ printf("N and K %d %d\n", *N, *K);
    }
    else if (RS1 == 0) { // Let glusterfs adapt to number of nodes pairs="6 4 11 8 12 8"
        if (number_of_nodes >= 12 && max_N > 11) {
            *N = 12;
            *K = 8;
        }
        else if (number_of_nodes >= 11 && max_N > 6) {
            *N = 11;
            *K = 8;
        }
        else {
            *N = 6;
            *K = 4;
        }
    }
    
    
    if (*N > max_N) {
        *K = -1;
        *N = -1;
        gettimeofday(&end, NULL);
        seconds  = end.tv_sec  - start.tv_sec;
                    useconds = end.tv_usec - start.tv_usec;
                    *total_scheduling_time += seconds + useconds/1000000.0;
        return;
    }
    
    qsort(nodes, number_of_nodes, sizeof(Node), compare_nodes_by_bandwidth_desc_with_condition);
    //~ print_nodes(nodes, number_of_nodes);
    double chunk_size = size / *K;
    //~ printf("chunk size %f\n", chunk_size);
    
    int* set_of_nodes_chosen_temp = (int*)malloc(*N * sizeof(int));
    if (set_of_nodes_chosen_temp == NULL) {
        perror("Failed to allocate memory");
        exit(EXIT_FAILURE);
    }
    
    // Choose top N nodes based on sorted bandwidths
    for (int i = 0; i < *N; i++) {
        set_of_nodes_chosen_temp[i] = i;
        //~ printf("%d ", i);
    }
    //~ printf("\n");
    
    // Check if the data would fit in chosen nodes
    int j = 0;
    for (int i = 0; i < *N; i++) {
        if (nodes[set_of_nodes_chosen_temp[i]].storage_size - chunk_size < 0) {
            int replace_ok = 0;
            for (int k = 0; k < number_of_nodes; k++) {
                //~ if (k != set_of_nodes_chosen_temp[i]) {
                if (!in_array(set_of_nodes_chosen_temp, *N, k)) {
                    if (nodes[k].storage_size - chunk_size >= 0) {
                        set_of_nodes_chosen_temp[i] = k;
                        replace_ok = 1;
                        break;
                    }
                }
            }
            if (!replace_ok) {
                //~ printf
                //~ free(set_of_nodes);
                free(set_of_nodes_chosen_temp);
                *N = -1;
                *K = -1;
                gettimeofday(&end, NULL);
                seconds  = end.tv_sec  - start.tv_sec;
                useconds = end.tv_usec - start.tv_usec;
                *total_scheduling_time += seconds + useconds/1000000.0;

                return;
            }
        }
        j++;
    }
    
    double* reliability_of_nodes_chosen = extract_reliabilities_of_chosen_nodes(nodes, number_of_nodes, set_of_nodes_chosen_temp, *N);

    // Check if the reliability threshold is met
    int loop = 0;
    //~ while (!reliability_threshold_met(N, 1, reliability_threshold, reliability_of_nodes_chosen)) {
    while (!reliability_threshold_met_accurate(*N, *K, reliability_threshold, reliability_of_nodes_chosen)) {
        if (loop > number_of_nodes - *N) {
            if (is_daos == true) {
                if (RS1 == 1) {
                    //~ printf("Swicth to RS1 = 2\n");
                    RS1 = 2;
                    goto start;
                }
                else if (RS1 == 2) {
                    //~ printf("Swicth to 4 rep now\n");
                    RS1 = 3;
                    goto start;
                }
                else if (RS1 == 3) {
                    //~ printf("Swicth to 6 rep now\n");
                    RS1 = 4;
                    goto start;
                }
            }
            free(set_of_nodes_chosen_temp);
            free(reliability_of_nodes_chosen);
            *N= -1;
            *K = -1;
            gettimeofday(&end, NULL);
            seconds  = end.tv_sec  - start.tv_sec;
            useconds = end.tv_usec - start.tv_usec;
            *total_scheduling_time += seconds + useconds/1000000.0;

            return;
        }
        
        // Find the lowest reliability node
        int index_min_reliability = 0;
        double min_reliability = reliability_of_nodes_chosen[0];
        for (int i = 1; i < *N; i++) {
            if (reliability_of_nodes_chosen[i] > min_reliability) {
                min_reliability = reliability_of_nodes_chosen[i];
                index_min_reliability = i;
            }
        }
        
        // Find the highest reliability node not in the chosen set
        int index_max_reliability = 0;
        double max_reliability = DBL_MAX;
        for (int i = 0; i < number_of_nodes; i++) {
            if (nodes[i].probability_failure < max_reliability && !in_array(set_of_nodes_chosen_temp, *N, i) && nodes[i].storage_size >= chunk_size) {
                max_reliability = nodes[i].probability_failure;
                index_max_reliability = i;
            }
        }
        
        // Replace the lowest reliability node with the best available node
        reliability_of_nodes_chosen[index_min_reliability] = max_reliability;
        set_of_nodes_chosen_temp[index_min_reliability] = index_max_reliability;
        
        loop++;
    }
    
                
                double min_write_bandwidth = DBL_MAX;
                double min_read_bandwidth = DBL_MAX;
                
                // Writing down the results
                double total_upload_time_to_print = 0;
                
                /** Read **/
                double total_read_time_to_print = 0;
                double total_read_time_parralelized_to_print = 0;
                double reconstruct_time = 0;

                *number_of_data_stored += 1;
                *total_N += *N;
                *total_storage_used += chunk_size*(*N);
                *size_stored += size;
                
                int* used_combinations = malloc(*N * sizeof(int));
                
                //~ printf("%f, %f, %d, %d, ", size, chunk_size, *N, *K);
                
                for (int j = 0; j < *N; j++) {
                    total_upload_time_to_print += chunk_size/nodes[set_of_nodes_chosen_temp[j]].write_bandwidth;
                    
                    /** Read **/
                    total_read_time_to_print += chunk_size/nodes[set_of_nodes_chosen_temp[j]].read_bandwidth;
                    
                    nodes[set_of_nodes_chosen_temp[j]].storage_size -= chunk_size;
                    
                    //~ printf("%d ", nodes[set_of_nodes_chosen_temp[j]].id);
                    
                    //~ printf("Removing %f from node %d\n", chunk_size, nodes[set_of_nodes_chosen_temp[j]].id);
                    if (min_write_bandwidth > nodes[set_of_nodes_chosen_temp[j]].write_bandwidth) {
                        min_write_bandwidth = nodes[set_of_nodes_chosen_temp[j]].write_bandwidth;
                    }
                    if (min_read_bandwidth > nodes[set_of_nodes_chosen_temp[j]].read_bandwidth) {
                        min_read_bandwidth = nodes[set_of_nodes_chosen_temp[j]].read_bandwidth;
                    }
                    
                    // To track the chunks I a fill a temp struct with nodes
                    used_combinations[j] = nodes[set_of_nodes_chosen_temp[j]].id;
                }
                
                //~ printf("\n");
                
                // Adding the chunks in the chosen nodes
                add_shared_chunks_to_nodes(used_combinations, *N, data_id, chunk_size, nodes, number_of_nodes, size);

                //~ *total_parralelized_upload_time += chunk_size/min_write_bandwidth;
                *total_parralelized_upload_time += fmax(size/out_going_bandwidth, chunk_size/min_write_bandwidth);
                
                /** Read **/
                //~ total_read_time_parralelized_to_print = chunk_size/min_read_bandwidth;
                total_read_time_parralelized_to_print = fmax(size/out_going_bandwidth, chunk_size/min_read_bandwidth);
                reconstruct_time = predict_reconstruct(models_reconstruct[closest_index], *N, *K, nearest_size, size);
        
                // TODO: remove this 3 lines under to reduce complexity if we don't need the trace per data
                double chunking_time = predict(models[closest_index], *N, *K, nearest_size, size);
                double transfer_time_parralelized = calculate_transfer_time(chunk_size, min_write_bandwidth);
                add_node_to_print(list, data_id, size, total_upload_time_to_print, transfer_time_parralelized, chunking_time, *N, *K, total_read_time_to_print, total_read_time_parralelized_to_print, reconstruct_time);
                
                /** Read **/
            *total_read_time_parrallelized += total_read_time_parralelized_to_print;
            *total_read_time += total_read_time_to_print;

                *total_upload_time += total_upload_time_to_print;
                
                free(used_combinations);
                free(set_of_nodes_chosen_temp);
                free(reliability_of_nodes_chosen);

                gettimeofday(&end, NULL);
                seconds  = end.tv_sec  - start.tv_sec;
                useconds = end.tv_usec - start.tv_usec;
                *total_scheduling_time += seconds + useconds/1000000.0;
                return;
            //~ }
            
        free(set_of_nodes_chosen_temp);
    free(reliability_of_nodes_chosen);
    
//~ }
    gettimeofday(&end, NULL);
    seconds  = end.tv_sec  - start.tv_sec;
    useconds = end.tv_usec - start.tv_usec;
    *total_scheduling_time += seconds + useconds/1000000.0;
}
