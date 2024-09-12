#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <stdbool.h>
#include <sys/time.h>
#include <../schedulers/algorithm4.h>
#include "../utils/prediction.h"
 
void optimal_schedule(int number_of_nodes, Node* nodes, float reliability_threshold, double size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, int* total_N, int closest_index, LinearModel* models, LinearModel* models_reconstruct, int nearest_size, DataList* list, int data_id, int max_N, double* total_read_time_parrallelized, double* total_read_time, Combination **combinations, int total_combinations, double* best_upload_time_to_print, double* best_read_time_to_print, double* size_stored) {
    *N = -1;
    *K = -1;
    
    int temp_N = 0;
    //~ int i = 0;
    int max_N_that_matches_reliability = -1;
    int max_K_that_matches_reliability = -1;
    //~ int best_N_for_upload = -1;
    int best_K_for_upload = -1;
    //~ int best_N_for_read = -1;
    int best_K_for_read = -1;
    double temp_best_upload_time = DBL_MAX;
    double temp_best_read_time = DBL_MAX;
    double best_upload_time = DBL_MAX;
    double best_read_time = DBL_MAX;
    double chunk_size = 0;
    
    // Get max speed for upload
    qsort(nodes, number_of_nodes, sizeof(Node), compare_nodes_by_bandwidth_desc_with_condition);
    //~ print_nodes(nodes, number_of_nodes);
    double total_upload_time_to_print = 0;
    double transfer_time_parralelized = 0;
    double temp_transfer_time_parralelized = 0;
    double temp_chunking_time = 0;
    double chunking_time = 0;
    
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
        }
        
        // Get speed for the selected nodes
        double min_write_bandwidth_of_nodes_chosen = nodes[set_of_nodes_chosen_temp[temp_N-1]].write_bandwidth;
        
        *K = get_max_K_from_reliability_threshold_and_nodes_chosen(temp_N, reliability_threshold, 0, 0, reliability_of_nodes_chosen);
        
        chunk_size = size/(*K);
        temp_transfer_time_parralelized = calculate_transfer_time(chunk_size, min_write_bandwidth_of_nodes_chosen);
        temp_best_upload_time = temp_transfer_time_parralelized;
        temp_chunking_time = predict(models[closest_index], temp_N, *K, nearest_size, size);
        temp_best_upload_time += temp_chunking_time;
        
        if (*K != -1 && temp_best_upload_time < best_upload_time) {
            best_upload_time = temp_best_upload_time;
            
            total_upload_time_to_print = 0;
            transfer_time_parralelized = temp_transfer_time_parralelized;
            chunking_time = temp_chunking_time;
            for (int i = 0; i < temp_N; i++) {
                total_upload_time_to_print += (size/(*K))/nodes[set_of_nodes_chosen_temp[i]].write_bandwidth;
            }
        
            //~ best_N_for_upload = temp_N;
            best_K_for_upload = *K;
        }
    }
    
    // Get max speed for read
    //~ printf("Sort by read bandwidth\n");
    qsort(nodes, number_of_nodes, sizeof(Node), compare_nodes_by_read_bandwidth_desc_with_condition);
    //~ print_nodes(nodes, number_of_nodes);
    double total_read_time_parralelized_to_print = 0;
    //~ double temp_total_read_time_parralelized_to_print = 0;
    double total_read_time_to_print = 0;
    double reconstruct_time = 0;
    double temp_reconstruct_time = 0;
    
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
        }
        
        // Get speed for the selected nodes
        double min_read_bandwidth_of_nodes_chosen = nodes[set_of_nodes_chosen_temp[temp_N-1]].read_bandwidth;
        
        *K = get_max_K_from_reliability_threshold_and_nodes_chosen(temp_N, reliability_threshold, 0, 0, reliability_of_nodes_chosen);
        
        chunk_size = size/(*K);
        temp_best_read_time = calculate_transfer_time(chunk_size, min_read_bandwidth_of_nodes_chosen);
        temp_reconstruct_time = predict_reconstruct(models_reconstruct[closest_index], temp_N, *K, nearest_size, size);
        temp_best_read_time += temp_reconstruct_time;
        
        if (*K != -1 && temp_best_read_time < best_read_time) {
            best_read_time = temp_best_read_time;
            
            reconstruct_time = temp_reconstruct_time;
            total_read_time_to_print = 0;
            for (int i = 0; i < temp_N; i++) {
                total_read_time_to_print += (size/(*K))/nodes[set_of_nodes_chosen_temp[i]].read_bandwidth;
            }
            total_read_time_parralelized_to_print = calculate_transfer_time(chunk_size, min_read_bandwidth_of_nodes_chosen);

            best_K_for_read = *K;
        }
    }

    // Get max reliability to min storage
    qsort(nodes, number_of_nodes, sizeof(Node), compare_nodes_by_reliability_desc_with_condition);
    
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
        }
        
        *K = get_max_K_from_reliability_threshold_and_nodes_chosen(temp_N, reliability_threshold, 0, 0, reliability_of_nodes_chosen);
        
        if (*K != -1) {
            max_N_that_matches_reliability = temp_N;
            max_K_that_matches_reliability = *K;
            break;
        }
    }
    
    //~ printf("%d %d %d\n", max_K_that_matches_reliability,best_K_for_upload,best_K_for_read);
    if (max_K_that_matches_reliability != -1 && best_K_for_upload != -1 && best_K_for_read != -1) {
        add_node_to_print(list, data_id, size, total_upload_time_to_print, transfer_time_parralelized, chunking_time, max_N_that_matches_reliability, max_K_that_matches_reliability, total_read_time_to_print, total_read_time_parralelized_to_print, reconstruct_time);

        chunk_size = size/(max_K_that_matches_reliability);
        *number_of_data_stored += 1;
        *total_storage_used += chunk_size*(max_N_that_matches_reliability);
        *size_stored += size;
        //~ printf("%d %d\n", max_N_that_matches_reliability, max_K_that_matches_reliability);
        //~ *best_upload_time_to_print += best_upload_time;
        *best_upload_time_to_print += fmax(size/out_going_bandwidth, best_upload_time);
        
        //~ *best_read_time_to_print += best_read_time;
        *best_read_time_to_print += fmax(size/out_going_bandwidth, best_read_time);
        *K = max_K_that_matches_reliability;
        *N = max_N_that_matches_reliability;
    }
}
