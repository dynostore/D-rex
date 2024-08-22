#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <stdbool.h>
#include <string.h>
#include <sys/time.h>
#include <../schedulers/algorithm4.h>
#include <../schedulers/random.h>
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

void hdfs_3_replications(int number_of_nodes, Node* nodes, float reliability_threshold, double size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, int closest_index, LinearModel* models, int nearest_size, DataList* list, int data_id) {
    struct timeval start, end;
    gettimeofday(&start, NULL);
    long seconds, useconds;
    printf("Start of hdfs_3_replications with data of size %f\n", size);
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
    print_nodes(nodes, number_of_nodes);
    
    // Take first 3 nodes with more than 128 MB
    int* set_of_nodes_chosen = malloc(3 * sizeof(int));    
    // TODO: attention de bien prendre les id ?
    // Ou pas besoin si c'est sort normalement
    for (i = 0; i < number_of_nodes; i++) {
        if (nodes[i].storage_size > 128) {
            set_of_nodes_chosen[j] = i;
            j++;
            if (j == 3) {
                break;
            }
        }
    }
    
    printf("Initial set of nodes chosen as index in sorted tab: ");
    for (i = 0; i < 3; i++) {
        printf("%d (%d) ", set_of_nodes_chosen[i], nodes[set_of_nodes_chosen[i]].write_bandwidth);
    }
    printf("\n");
    //~ exit(1);
    int index_max_reliability = 0;
    double max_reliability = DBL_MAX; // Initialize to a value lower than any reliability value
    int loop = 0;
    double* reliability_of_nodes_chosen;
    reliability_of_nodes_chosen = extract_reliabilities_of_chosen_nodes(nodes, number_of_nodes, set_of_nodes_chosen, 3);
    
    printf("Initial reliability: ");
    for (i = 0; i < 3; i++) {
        printf("%f = %f ", nodes[set_of_nodes_chosen[i]].probability_failure, reliability_of_nodes_chosen[i]);
    }
    printf("\n");
    //~ exit(1);
    
    while (!reliability_threshold_met_accurate(3, 1, reliability_threshold, reliability_of_nodes_chosen)) {
        printf("Reliability not met with initial set\n");
        if (loop > number_of_nodes - 3) {
            free(reliability_of_nodes_chosen);
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
    }
    
    printf("Set of nodes chosen as index in sorted tab after reliability check: ");
    for (i = 0; i < 3; i++) {
        printf("%d (%d) ", set_of_nodes_chosen[i], nodes[set_of_nodes_chosen[i]].write_bandwidth);
    }
    printf("\n");
        printf("New reliability: ");
    for (i = 0; i < 3; i++) {
        printf("%f = %f ", nodes[set_of_nodes_chosen[i]].probability_failure, reliability_of_nodes_chosen[i]);
    }
    printf("\n");
    //~ exit(1);
    
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
    printf("rest_to_store = %f\n", rest_to_store);
    for (i = 0; i < 3; i++) {
        printf("%f ", size_to_stores[i]);
    }
    printf("\n"); 
    //~ exit(1);
    if (rest_to_store != 0) { // We have leftovers to put on a fourth node or more
        all_good = false;
        for (j = 0; j < number_of_nodes; j++) {
            printf("j = %d\n", j);
            //~ i = set_of_nodes[j];
            i = j;
            bool already_chosen = false;
            for (k = 0; k < num_nodes_chosen; k++) {
                if (i == set_of_nodes_chosen[k]) {
                    already_chosen = true;
                    printf("break\n");
                    break;
                }
            }
        
            if (!already_chosen && nodes[i].storage_size > 128) {
                //~ set_of_nodes_chosen[num_nodes_chosen++] = i;
                printf("add\n");
                add_node_to_set(&set_of_nodes_chosen, &num_nodes_chosen, i);
                
                printf("Set of nodes chosen as index in sorted tab after adding a node: ");
                for (int ii = 0; ii < *N+1; ii++) {
                    printf("%d (%d) ", set_of_nodes_chosen[ii], nodes[set_of_nodes_chosen[ii]].write_bandwidth);
                }
                printf("\n");
                //~ exit(1);
                //~ double reliability_of_nodes_chosen[num_nodes_chosen];
                //~ for (k = 0; k < num_nodes_chosen; k++) {
                    //~ reliability_of_nodes_chosen[k] = reliability_of_nodes[set_of_nodes_chosen[k]];
                //~ }
                free(reliability_of_nodes_chosen);
                *N += 1;
                *K += 1;
                reliability_of_nodes_chosen = extract_reliabilities_of_chosen_nodes(nodes, number_of_nodes, set_of_nodes_chosen, *N);

                if (reliability_threshold_met_accurate(*N, *K, reliability_threshold, reliability_of_nodes_chosen)) {
                    printf("ok\n");
                    if (rest_to_store <= nodes[i].storage_size) {
                        size_to_stores[num_nodes_chosen - 1] = rest_to_store;
                        all_good = true;
                            //~ printf("rest_to_store = %f\n", rest_to_store);
                        for (int ii = 0; ii < num_nodes_chosen; ii++) {
                            printf("%f ", size_to_stores[ii]);
                        }
                        printf("\n");
                        printf("break\n");
                        break;
                    } else { // Need again another node
                        printf("else\n");
                        rest_to_store -= nodes[i].storage_size;
                        size_to_stores[num_nodes_chosen - 1] = nodes[i].storage_size;
                    }
                } else {
                    printf("else\n");
                    *K -= 1;
                    *N -= 1;
                    //~ num_nodes_chosen--;
                    //~ printf("%d\n", num_nodes_chosen);
                    //~ remove_node_from_set(&set_of_nodes_chosen, &num_nodes_chosen, i);
                    remove_last_node(&set_of_nodes_chosen, &num_nodes_chosen);                    
                    printf("Set of nodes chosen as index in sorted tab after removing a node: ");
                    for (int ii = 0; ii < *N; ii++) {
                        printf("%d (%d) ", set_of_nodes_chosen[ii], nodes[set_of_nodes_chosen[ii]].write_bandwidth);
                    }
                    printf("\n");
                    
                }
            }
        }
              //~ printf("Set of nodes chosen as index in sorted tab after adding a node: ");
    //~ for (i = 0; i < *N+1; i++) {
        //~ printf("%d (%d) ", set_of_nodes_chosen[i], nodes[set_of_nodes_chosen[i]].write_bandwidth);
    //~ }
    //~ printf("\n"); exit(1);
        if (!all_good) {
            printf("Not good\n");
            // Need to loop and find a solution that works in terms of reliability
            for (i = 0; i < number_of_nodes - 2; i++) {
                for (j = i + 1; j < number_of_nodes - 1; j++) {
                    for (k = j + 1; k < number_of_nodes; k++) {
                        int temp_set[] = {i, j, k};
                        //~ double temp_reliability[] = {reliability_of_nodes[i], reliability_of_nodes[j], reliability_of_nodes[k]};
                        double* temp_reliability = extract_reliabilities_of_chosen_nodes(nodes, number_of_nodes, set_of_nodes_chosen, *N);
                        if (reliability_threshold_met_accurate(3, 1, reliability_threshold, temp_reliability)) { // replace 0.95 with actual threshold
                            double temp_size_to_stores[3];
                            bool all_good_2 = true;
                            for (l = 0; l < 3; l++) {
                                int index = temp_set[l];
                                if (size <= nodes[index].storage_size) { // all fit
                                    temp_size_to_stores[l] = size;
                                } else {
                                    all_good_2 = false;
                                    break;
                                }
                            }
                            if (all_good_2) {
                                memcpy(size_to_stores, temp_size_to_stores, sizeof(temp_size_to_stores));
                                all_good = true;
                                break;
                            }
                        }
                    }
                    if (all_good) break;
                }
                if (all_good) break;
            }

            if (!all_good) {
                printf("Error: size HDFS 3 replications failed\n");
                free(reliability_of_nodes_chosen);
                gettimeofday(&end, NULL);
                seconds  = end.tv_sec  - start.tv_sec;
                useconds = end.tv_usec - start.tv_usec;
                *total_scheduling_time += seconds + useconds/1000000.0;
                return;
            }
        }
    }
    printf("Updates %d %d %d\n", *N, *K, num_nodes_chosen);
    // Updates
    if (*N != -1) { // We have a valid solution        
        double worst_transfer = -1;
        
        // Writing down the results
        double total_upload_time_to_print = 0;
        //~ double chunk_size = size/(*K);
        *number_of_data_stored += 1;
        *total_N += *N;
        *total_storage_used += size*3;
        Node** used_combinations = malloc(*N * sizeof(Node*));
        
        for (int j = 0; j < *N; j++) {
            total_upload_time_to_print += size_to_stores[j]/nodes[set_of_nodes_chosen[j]].write_bandwidth;
            nodes[set_of_nodes_chosen[j]].storage_size -= size_to_stores[j];
            printf("Removed %f from node %d\n", size_to_stores[j], nodes[set_of_nodes_chosen[j]].id); 
            
            if (worst_transfer > size_to_stores[j]/nodes[set_of_nodes_chosen[j]].write_bandwidth) {
                worst_transfer = size_to_stores[j]/nodes[set_of_nodes_chosen[j]].write_bandwidth;
            }
            
            // To track the chunks I a fill a temp struct with nodes
            used_combinations[j] = &nodes[set_of_nodes_chosen[j]];
        }
        
        // Adding the chunks in the chosen nodes
        //~ add_shared_chunks_to_nodes(used_combinations, *N, data_id);
        
        *total_parralelized_upload_time += worst_transfer;
        
        // TODO: remove this 3 lines under to reduce complexity if we don't need the trace per data
        double chunking_time = predict(models[closest_index], *N, *K, nearest_size, size);
        double transfer_time_parralelized = worst_transfer;
        add_node_to_print(list, data_id, size, total_upload_time_to_print, transfer_time_parralelized, chunking_time, *N, *K);
        *total_upload_time += total_upload_time_to_print;
    }

    //~ exit(1);
    gettimeofday(&end, NULL);
    seconds  = end.tv_sec  - start.tv_sec;
    useconds = end.tv_usec - start.tv_usec;
    *total_scheduling_time += seconds + useconds/1000000.0;
}

void hdfs_rs(int number_of_nodes, Node* nodes, float reliability_threshold, double size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, int closest_index, LinearModel* models, int nearest_size, DataList* list, int data_id, int RS1, int RS2) {
    struct timeval start, end;
    gettimeofday(&start, NULL);
    long seconds, useconds;
    
    int i = 0;
    *N = -1;
    *K = -1;
    gettimeofday(&end, NULL);
    seconds  = end.tv_sec  - start.tv_sec;
    useconds = end.tv_usec - start.tv_usec;
    *total_scheduling_time += seconds + useconds/1000000.0;
}
