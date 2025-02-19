#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <stdbool.h>
#include <string.h>
#include <sys/time.h>
#include <../schedulers/algorithm4.h>
#include <../schedulers/random.h>
#include <../schedulers/glusterfs.h>
#include "../utils/prediction.h"

void add_node_to_set(int** set_of_nodes_chosen, int* num_nodes_chosen, int new_node) {
    // Increment the number of nodes
    (*num_nodes_chosen)++;

    // Reallocate memory to accommodate the new node
    int* temp = realloc(*set_of_nodes_chosen, (*num_nodes_chosen) * sizeof(int));
    if (temp == NULL) {
        fprintf(stderr, "Memory allocation failed!\n");
        exit(EXIT_FAILURE);
    }
    *set_of_nodes_chosen = temp;

    // Add the new node to the end of the array
    (*set_of_nodes_chosen)[*num_nodes_chosen - 1] = new_node;
}

void remove_last_node(int** set_of_nodes_chosen, int* num_nodes_chosen) {
    // Decrease the number of nodes
    (*num_nodes_chosen)--;

    // Reallocate memory to the new size (one less element)
    *set_of_nodes_chosen = realloc(*set_of_nodes_chosen, (*num_nodes_chosen) * sizeof(int));

    // Check if realloc was successful
    if (*set_of_nodes_chosen == NULL && *num_nodes_chosen > 0) {
        fprintf(stderr, "Memory reallocation failed!\n");
        exit(EXIT_FAILURE);
    }
}

void hdfs_3_replications(int number_of_nodes, Node* nodes, float reliability_threshold, double size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, int closest_index, LinearModel* models, LinearModel* models_reconstruct, int nearest_size, DataList* list, int data_id, int max_N, double* total_read_time_parrallelized, double* total_read_time, double* size_stored) {
    struct timeval start, end;
    gettimeofday(&start, NULL);
    long seconds, useconds;
    //~ printf("Start of hdfs_3_replications with data of size %f with %d nodes\n", size, number_of_nodes);
    int i = 0;
    int j = 0;
    int k = 0;
    int l = 0;
    double min_reliability = -1; // Use a large value to start with
    int index_min_reliability = 0;
    *N = -1;
    *K = -1;
    
    // Sort by BW
    qsort(nodes, number_of_nodes, sizeof(Node), compare_nodes_by_bandwidth_desc_with_condition);
    //~ print_nodes(nodes, number_of_nodes);
    
    // Take first 3 nodes with more than 128 MB
    int* set_of_nodes_chosen = malloc(number_of_nodes * sizeof(int)); // We alloc more but keep track of how many node we actually use
    double* reliability_of_nodes_chosen = malloc(number_of_nodes * sizeof(double));
    
    for (i = 0; i < number_of_nodes; i++) {
        set_of_nodes_chosen[i] = -1; // To signify that it is not valid
        reliability_of_nodes_chosen[i] = -1; // To signify that it is not valid
        //~ printf("%f\n", nodes[i].storage_size);
        if ((nodes[i].storage_size > 128 || size <= nodes[i].storage_size) && j < 3) {
            set_of_nodes_chosen[j] = i;
            reliability_of_nodes_chosen[j] = nodes[set_of_nodes_chosen[j]].probability_failure;
            j++;
        }
    }
    //~ printf("set chosen %d %d %d\n", set_of_nodes_chosen[0], set_of_nodes_chosen[1], set_of_nodes_chosen[2]);
    
    for (i = 0; i < 3; i++) {
        if (set_of_nodes_chosen[i] == -1) {
            free(reliability_of_nodes_chosen);
            free(set_of_nodes_chosen);
            *K = -1;
            *N = -1;
            gettimeofday(&end, NULL);
            seconds  = end.tv_sec  - start.tv_sec;
            useconds = end.tv_usec - start.tv_usec;
            *total_scheduling_time += seconds + useconds/1000000.0;
            return;
        }
    }
    
    int index_max_reliability = 0;
    double max_reliability = DBL_MAX; // Initialize to a value lower than any reliability value
    int loop = 0;
    //~ double* reliability_of_nodes_chosen = malloc(number_of_nodes * sizeof(int));
    //~ reliability_of_nodes_chosen = extract_reliabilities_of_chosen_nodes(nodes, number_of_nodes, set_of_nodes_chosen, 3);
    
    while (!reliability_threshold_met_accurate(3, 1, reliability_threshold, reliability_of_nodes_chosen)) {
        if (loop > number_of_nodes - 3) {
            free(reliability_of_nodes_chosen);
            free(set_of_nodes_chosen);
            *K = -1;
            *N = -1;
            gettimeofday(&end, NULL);
            seconds  = end.tv_sec  - start.tv_sec;
            useconds = end.tv_usec - start.tv_usec;
            *total_scheduling_time += seconds + useconds/1000000.0;
            return;
        }
        
        for (i = 0; i < 3; i++) {
            if (min_reliability < reliability_of_nodes_chosen[i]) {
                min_reliability = reliability_of_nodes_chosen[i];
                index_min_reliability = i;
            }
        }
        
        // Find the index of the highest new reliability value not already in set_of_nodes_chosen
        for (i = 0; i < number_of_nodes; i++) {
            bool already_chosen = false;
            for (j = 0; j < 3; j++) {
                if (i == set_of_nodes_chosen[j]) {
                    already_chosen = true;
                    break;
                }
            }

            if (!already_chosen && nodes[i].probability_failure < max_reliability && nodes[i].storage_size > 128) {
                max_reliability = nodes[i].probability_failure;
                index_max_reliability = i;
            }
        }

        // Replace the lowest reliability value with the new maximum reliability value
        reliability_of_nodes_chosen[index_min_reliability] = max_reliability;

        // Update the corresponding node in set_of_nodes_chosen
        set_of_nodes_chosen[index_min_reliability] = index_max_reliability;
        
        loop++;
    }
    
    *N = 3;
    *K = 1;
    double* size_to_stores = malloc(number_of_nodes*sizeof(int));
    double rest_to_store = 0;
    bool all_good = false;
    for (j = 0; j < 3; j++) {
        i = set_of_nodes_chosen[j];
        if (size <= nodes[i].storage_size) { // all fit
            size_to_stores[j] = size;
        } else { // all doesn't fit so put as much as possible and we'll put the rest on another node
            rest_to_store += size - nodes[i].storage_size;
            size_to_stores[j] = nodes[i].storage_size;
        }
    }
    int num_nodes_chosen = 3;

    if (rest_to_store != 0) { // We have leftovers to put on a fourth node or more
        all_good = false;
        for (j = 0; j < number_of_nodes; j++) {
            i = j;
            bool already_chosen = false;
            for (k = 0; k < num_nodes_chosen; k++) {
                if (i == set_of_nodes_chosen[k]) {
                    already_chosen = true;
                    break;
                }
            }
        
            if (!already_chosen && nodes[i].storage_size > 128) {
                //~ set_of_nodes_chosen[num_nodes_chosen++] = i;
                //~ printf("add\n");
                //~ add_node_to_set(&set_of_nodes_chosen, &num_nodes_chosen, i);
                set_of_nodes_chosen[num_nodes_chosen] = i;
                reliability_of_nodes_chosen[num_nodes_chosen] = nodes[i].probability_failure;
                
                num_nodes_chosen++;
                
                //~ printf("Set of nodes chosen as index in sorted tab after adding a node: ");
                
                *N += 1;
                *K += 1;
                
                if (*N > max_N) {
                    free(reliability_of_nodes_chosen);
                    free(set_of_nodes_chosen);
                    free(size_to_stores);
                    *K = -1;
                    *N = -1;
                    gettimeofday(&end, NULL);
                    seconds  = end.tv_sec  - start.tv_sec;
                    useconds = end.tv_usec - start.tv_usec;
                    *total_scheduling_time += seconds + useconds/1000000.0;
                    return;
                }
                    

                if (reliability_threshold_met_accurate(*N, *K, reliability_threshold, reliability_of_nodes_chosen)) {
                    if (rest_to_store <= nodes[i].storage_size) {
                        size_to_stores[num_nodes_chosen - 1] = rest_to_store;
                        all_good = true;
                        //~ for (int ii = 0; ii < num_nodes_chosen; ii++) {
                            //~ printf("%f ", size_to_stores[ii]);
                        //~ }
                        //~ printf("\n"); printf("break\n");
                        break;
                    } else { // Need again another node
                        rest_to_store -= nodes[i].storage_size;
                        size_to_stores[num_nodes_chosen - 1] = nodes[i].storage_size;
                    }
                } else {
                    *K -= 1;
                    *N -= 1;
                    
                    set_of_nodes_chosen[num_nodes_chosen] = -1;
                    reliability_of_nodes_chosen[num_nodes_chosen] = -1;
                    num_nodes_chosen--;
                }
            }
        }
              //~ printf("Set of nodes chosen as index in sorted tab after adding a node: ");
        //~ printf("%d (%d) ", set_of_nodes_chosen[i], nodes[set_of_nodes_chosen[i]].write_bandwidth);
    //~ }
        if (!all_good) {
            num_nodes_chosen = 3;
            *N = 3;
            *K = 1;
            // Need to loop and find a solution that works in terms of reliability
            for (i = 0; i < number_of_nodes - 2; i++) {
                for (j = i + 1; j < number_of_nodes - 1; j++) {
                    for (k = j + 1; k < number_of_nodes; k++) {
                        //~ int temp_set[] = {i, j, k};
                        //~ double temp_reliability[] = {reliability_of_nodes[i], reliability_of_nodes[j], reliability_of_nodes[k]};
                        set_of_nodes_chosen[0] = i;
                        set_of_nodes_chosen[1] = j;
                        set_of_nodes_chosen[2] = k;
                        //~ printf("set chosen %d %d %d\n", set_of_nodes_chosen[0], set_of_nodes_chosen[1], set_of_nodes_chosen[2]);
                        reliability_of_nodes_chosen[0] = nodes[i].probability_failure;
                        reliability_of_nodes_chosen[1] = nodes[j].probability_failure;
                        reliability_of_nodes_chosen[2] = nodes[k].probability_failure;
                        //~ printf("%d %d %d %f %f %f\n", i, j, k, reliability_of_nodes_chosen[0], reliability_of_nodes_chosen[1], reliability_of_nodes_chosen[2]);
                        
                        if (reliability_threshold_met_accurate(3, 1, reliability_threshold, reliability_of_nodes_chosen)) {
                            //~ double temp_size_to_stores[3]; // TODO a utiliser nan ?
                            bool all_good_2 = true;
                            for (l = 0; l < 3; l++) {
                                int index = set_of_nodes_chosen[l];
                                if (size <= nodes[index].storage_size) { // all fit
                                    size_to_stores[l] = size;
                                } else {
                                    all_good_2 = false;
                                    break;
                                }
                            }
                            if (all_good_2) {
                                all_good = true;
                                break;
                            }
                        }
                    }
                    if (all_good) break;
                }
                if (all_good) break;
            }
            //~ printf("0.\n");
            if (!all_good) {
                free(reliability_of_nodes_chosen);
                free(set_of_nodes_chosen);
                free(size_to_stores);
                *K = -1;
                *N = -1;
                gettimeofday(&end, NULL);
                seconds  = end.tv_sec  - start.tv_sec;
                useconds = end.tv_usec - start.tv_usec;
                *total_scheduling_time += seconds + useconds/1000000.0;
                return;
            }
            //~ printf("0.2.\n");
        }
    }
    
    if (*N > max_N) {
                    free(reliability_of_nodes_chosen);
                free(set_of_nodes_chosen);
                free(size_to_stores);
                *K = -1;
                *N = -1;
                gettimeofday(&end, NULL);
                seconds  = end.tv_sec  - start.tv_sec;
                useconds = end.tv_usec - start.tv_usec;
                *total_scheduling_time += seconds + useconds/1000000.0;
                return;
}
    //~ printf("1.\n");
    // Updates
    if (*N != -1) { // We have a valid solution 
        double worst_transfer = -1;
        double worst_transfer_read = -1;
        
        // Writing down the results
        double total_upload_time_to_print = 0;
        
        /** Read **/
        double total_read_time_to_print = 0;
        double total_read_time_parralelized_to_print = 0;
        double reconstruct_time = 0;

        *number_of_data_stored += 1;
        *total_N += *N;
        *total_storage_used += size*3;
        int* used_combinations = malloc(*N * sizeof(int));
        *size_stored += size;
        
        //~ printf("%f, %f, %d, %d, ", size, size, *N, *K);
        
        for (int j = 0; j < *N; j++) {
            total_upload_time_to_print += size_to_stores[j]/nodes[set_of_nodes_chosen[j]].write_bandwidth;
            
            /** Read **/
            total_read_time_to_print += size_to_stores[j]/nodes[set_of_nodes_chosen[j]].read_bandwidth;
                    
            nodes[set_of_nodes_chosen[j]].storage_size -= size_to_stores[j];
            //~ printf("Removed %f from node %d\n", size_to_stores[j], nodes[set_of_nodes_chosen[j]].id); 
            
            //~ printf("%d ", nodes[set_of_nodes_chosen[j]].id);
            
            if (worst_transfer < size_to_stores[j]/nodes[set_of_nodes_chosen[j]].write_bandwidth) {
                worst_transfer = size_to_stores[j]/nodes[set_of_nodes_chosen[j]].write_bandwidth;
            }
            if (worst_transfer_read < size_to_stores[j]/nodes[set_of_nodes_chosen[j]].read_bandwidth) {
                worst_transfer_read = size_to_stores[j]/nodes[set_of_nodes_chosen[j]].read_bandwidth;
            }
            
            // To track the chunks I a fill a temp struct with nodes
            used_combinations[j] = nodes[set_of_nodes_chosen[j]].id;
            //~ printf("%d\n", used_combinations[j]);
        }
        //~ printf("\n");
        
        // Adding the chunks in the chosen nodes
        add_shared_chunks_to_nodes_3_replication(used_combinations, *N, data_id, size_to_stores, nodes, number_of_nodes, size);
        
        //~ *total_parralelized_upload_time += worst_transfer;
        *total_parralelized_upload_time += fmax(size/out_going_bandwidth, worst_transfer);
        
        /** Read **/
        //~ total_read_time_parralelized_to_print = worst_transfer_read;
        total_read_time_parralelized_to_print = fmax(size/out_going_bandwidth, worst_transfer_read);
        reconstruct_time = predict_reconstruct(models_reconstruct[closest_index], *N, *K, nearest_size, size);
        
        // TODO: remove this 3 lines under to reduce complexity if we don't need the trace per data
        double chunking_time = predict(models[closest_index], *N, *K, nearest_size, size);
        double transfer_time_parralelized = worst_transfer;
        add_node_to_print(list, data_id, size, total_upload_time_to_print, transfer_time_parralelized, chunking_time, *N, *K, total_read_time_to_print, total_read_time_parralelized_to_print, reconstruct_time);
        
        /** Read **/
            *total_read_time_parrallelized += total_read_time_parralelized_to_print;
            *total_read_time += total_read_time_to_print;
        *total_upload_time += total_upload_time_to_print;
        
        free(used_combinations);
    }
    //~ printf("2.\n");
    free(reliability_of_nodes_chosen);
    free(set_of_nodes_chosen);
    free(size_to_stores);
    //~ printf("3.\n");
    gettimeofday(&end, NULL);
    seconds  = end.tv_sec  - start.tv_sec;
    useconds = end.tv_usec - start.tv_usec;
    *total_scheduling_time += seconds + useconds/1000000.0;
}

void hdfs_rs(int number_of_nodes, Node* nodes, float reliability_threshold, double size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, int closest_index, LinearModel* models, LinearModel* models_reconstruct, int nearest_size, DataList* list, int data_id, int RS1, int RS2, double* total_read_time_parrallelized, double* total_read_time, int max_N, double* size_stored) {
    struct timeval start, end;
    gettimeofday(&start, NULL);
    long seconds, useconds;

    *K = RS1;
    *N = RS1 + RS2;
    
    if (RS1 == 0) { // Let hdfs_rs adapt to number of nodes pairs="3 2 6 3 10 4"
        if (number_of_nodes >= 14 && max_N > 9) {
            *K = 10;
            *N = 10 + 4;
        }
        else if (number_of_nodes >= 9 && max_N > 5) {
            *K = 6;
            *N = 6 + 3;
        }
        else {
            *K = 3;
            *N = 3 + 2;
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
    
    //~ printf("%d %d\n", *N, *K);
    qsort(nodes, number_of_nodes, sizeof(Node), compare_nodes_by_bandwidth_desc_with_condition);
    //~ print_nodes(nodes, number_of_nodes);
    
    double chunk_size = size / *K;
    
    int* set_of_nodes_chosen_temp = (int*)malloc(*N * sizeof(int));
    if (set_of_nodes_chosen_temp == NULL) {
        perror("Failed to allocate memory");
        exit(EXIT_FAILURE);
    }
    
    // Choose top N nodes based on sorted bandwidths
    for (int i = 0; i < *N; i++) {
        set_of_nodes_chosen_temp[i] = i;
    }
    
    // Check if the data would fit in chosen nodes
    int j = 0;
    for (int i = 0; i < *N; i++) {
        if (nodes[set_of_nodes_chosen_temp[i]].storage_size - chunk_size < 0) {
            int replace_ok = 0;
            for (int k = 0; k < number_of_nodes; k++) {
                if (!in_array(set_of_nodes_chosen_temp, *N, k)) {
                    if (nodes[k].storage_size - chunk_size >= 0) {
                        set_of_nodes_chosen_temp[i] = k;
                        replace_ok = 1;
                        break;
                    }
                }
            }
            if (!replace_ok) {
                //~ printf("could not replace\n");
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
    while (!reliability_threshold_met_accurate(*N, *K, reliability_threshold, reliability_of_nodes_chosen)) {
        if (loop > number_of_nodes - *N) {
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
                
                //~ printf("%f, %f, %d, %d, ", size, chunk_size, *N, *K);
                
                int* used_combinations = malloc(*N * sizeof(int));
                
                for (int j = 0; j < *N; j++) {
                    total_upload_time_to_print += chunk_size/nodes[set_of_nodes_chosen_temp[j]].write_bandwidth;
                    
                    /** Read **/
                    total_read_time_to_print += chunk_size/nodes[set_of_nodes_chosen_temp[j]].read_bandwidth;
                    
                    //~ printf("%d ", nodes[set_of_nodes_chosen_temp[j]].id);
                    
                    nodes[set_of_nodes_chosen_temp[j]].storage_size -= chunk_size;
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

                if (size/out_going_bandwidth > chunk_size/min_write_bandwidth) { printf("Adding to parralel upload max of %f %f: %f\n", size/out_going_bandwidth, chunk_size/min_write_bandwidth, fmax(size/out_going_bandwidth, chunk_size/min_write_bandwidth)); }
                *total_parralelized_upload_time += fmax(size/out_going_bandwidth, chunk_size/min_write_bandwidth);
                //~ *total_parralelized_upload_time += chunk_size/min_write_bandwidth;
                
                /** Read **/
                //~ total_read_time_parralelized_to_print = chunk_size/min_read_bandwidth;
                total_read_time_parralelized_to_print = fmax(size/out_going_bandwidth, chunk_size/min_read_bandwidth);
                reconstruct_time = predict_reconstruct(models_reconstruct[closest_index], *N, *K, nearest_size, size);
        
                // TODO: remove this 3 lines under to reduce complexity if we don't need the trace per data
                double chunking_time = predict(models[closest_index], *N, *K, nearest_size, size);
                double transfer_time_parralelized = calculate_transfer_time(chunk_size, min_write_bandwidth);
                add_node_to_print(list, data_id, size, total_upload_time_to_print, transfer_time_parralelized, chunking_time, *N, *K, total_read_time_to_print, total_read_time_parralelized_to_print, reconstruct_time);

                *total_upload_time += total_upload_time_to_print;
                
                /** Read **/
                *total_read_time_parrallelized += total_read_time_parralelized_to_print;
                *total_read_time += total_read_time_to_print;
                
                free(set_of_nodes_chosen_temp);
                free(used_combinations);
                free(reliability_of_nodes_chosen);

                gettimeofday(&end, NULL);
                seconds  = end.tv_sec  - start.tv_sec;
                useconds = end.tv_usec - start.tv_usec;
                *total_scheduling_time += seconds + useconds/1000000.0;
                return;
            
    free(set_of_nodes_chosen_temp);
    free(reliability_of_nodes_chosen);
    
    gettimeofday(&end, NULL);
    seconds  = end.tv_sec  - start.tv_sec;
    useconds = end.tv_usec - start.tv_usec;
    *total_scheduling_time += seconds + useconds/1000000.0;
}
