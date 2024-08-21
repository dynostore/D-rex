#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <stdbool.h>
#include <sys/time.h>
#include <../schedulers/algorithm4.h>
#include <../schedulers/random.h>
#include "../utils/prediction.h"

void hdfs_3_replications(int number_of_nodes, Node* nodes, float reliability_threshold, double size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, int closest_index, LinearModel* models, int nearest_size, DataList* list, int data_id) {
    struct timeval start, end;
    gettimeofday(&start, NULL);
    long seconds, useconds;
    
    int i = 0;
    int j = 0;
    double min_reliability = __DBL_MAX__; // Use a large value to start with
    int index_min_reliability = 0;

    // Sort by BW
    qsort(nodes, number_of_nodes, sizeof(Node), compare_nodes_by_bandwidth_desc_with_condition);
    
    // Take first 3 nodes with more than 128 MB
    int* set_of_nodes_chosen = malloc(3*sizeof(int));
    
    // TODO: attention de bien prendre les id ?
    // Ou pas besoin si c'est sort normalement
    for (i = 0; i < number_of_nodes; i++) {
        if (nodes[i]->storage_size > 128;) {
            set_of_nodes_chosen[i] = j;
        }
        j++;
    }
    
    int index_max_reliability = 0;
    double max_reliability = -1.0; // Initialize to a value lower than any reliability value
    int loop = 0;
    double* reliability_of_nodes_chosen;
    reliability_of_nodes_chosen = extract_reliabilities_of_chosen_nodes(nodes, number_of_nodes, set_of_nodes_chosen, 3);
    
    while (!reliability_threshold_met_accurate(3, 1, reliability_threshold, reliability_of_nodes_chosen)) {
        if (loop > number_of_nodes - 3) {
            free(reliability_of_nodes_chosen);
            gettimeofday(&end, NULL);
            seconds  = end.tv_sec  - start.tv_sec;
            useconds = end.tv_usec - start.tv_usec;
            *total_scheduling_time += seconds + useconds/1000000.0;
            return;
        }
        
        
        // Find the index of the highest new reliability value not already in set_of_nodes_chosen
        for (int i = 0; i < num_nodes; i++) {
            bool already_chosen = false;
            for (int j = 0; j < num_chosen_nodes; j++) {
                if (set_of_nodes[i] == set_of_nodes_chosen[j]) {
                    already_chosen = true;
                    break;
                }
            }

            if (!already_chosen && reliability_of_nodes[i] > max_reliability) {
                max_reliability = reliability_of_nodes[i];
                index_max_reliability = i;
            }
        }

        // Replace the lowest reliability value with the new maximum reliability value
        reliability_of_nodes_chosen[index_min_reliability] = max_reliability;

        // Update the corresponding node in set_of_nodes_chosen
        set_of_nodes_chosen[index_min_reliability] = set_of_nodes[index_max_reliability]; 
        
               
    }
    
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
    
    gettimeofday(&end, NULL);
    seconds  = end.tv_sec  - start.tv_sec;
    useconds = end.tv_usec - start.tv_usec;
    *total_scheduling_time += seconds + useconds/1000000.0;
}
