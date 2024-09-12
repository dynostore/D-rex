#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <stdbool.h>
#include <sys/time.h>
#include <time.h>
#include <../schedulers/algorithm4.h>
#include "../utils/prediction.h"

bool nodes_can_fit_new_data(int* set_of_nodes_chosen, int number_of_nodes_chosen, double chunk_size, Node* nodes) {
    for (int i = 0; i < number_of_nodes_chosen; i++) {
        int node_index = set_of_nodes_chosen[i];
        if (nodes[node_index].storage_size < chunk_size) {
            return false;
        }
    }
    return true;
}

double* extract_reliabilities_of_chosen_nodes(Node* nodes, int total_nodes, int* set_of_nodes_chosen, int num_chosen) {
    // Allocate memory for the result array
    double* reliabilities = malloc(num_chosen * sizeof(double));
    if (reliabilities == NULL) {
        // Handle memory allocation failure
        perror("Failed to allocate memory for reliabilities");
        exit(EXIT_FAILURE);
    }

    // Extract the reliability values of the nodes chosen
    for (int i = 0; i < num_chosen; i++) {
        int node_index = set_of_nodes_chosen[i];
        if (node_index >= 0 && node_index < total_nodes) {
            reliabilities[i] = nodes[node_index].probability_failure;
        }
        else {
            // Handle out-of-bounds index (optional)
            printf("Node index %d out of bounds", node_index);
            free(reliabilities);
            exit(EXIT_FAILURE);
        }
    }

    return reliabilities;
}

void get_random_sample(int* result, int number_of_nodes, int N) {
    int* available = (int*)malloc(number_of_nodes * sizeof(int));
    if (available == NULL) {
        perror("Failed to allocate memory");
        exit(EXIT_FAILURE);
    }

    // Initialize the array with numbers from 0 to number_of_nodes - 1
    for (int i = 0; i < number_of_nodes; i++) {
        available[i] = i;
    }

    // Shuffle the array
    for (int i = number_of_nodes - 1; i > 0; i--) {
        int j = rand() % (i + 1);
        int temp = available[i];
        available[i] = available[j];
        available[j] = temp;
    }

    // Copy the first N elements to the result
    for (int i = 0; i < N; i++) {
        result[i] = available[i];
    }

    free(available);
}

// Utility function to get a random number excluding the already looked at numbers
int get_random_excluding_exclusions(int number_of_nodes, int* already_looked_at, int already_looked_at_count) {
    int* valid_choices = (int*)malloc(number_of_nodes * sizeof(int));
    int valid_count = 0;
    
    for (int i = 2; i <= number_of_nodes; i++) {
        int found = 0;
        for (int j = 0; j < already_looked_at_count; j++) {
            if (already_looked_at[j] == i) {
                found = 1;
                break;
            }
        }
        if (!found) {
            valid_choices[valid_count++] = i;
        }
    }

    if (valid_count == 0) {
        free(valid_choices);
        return -1;
    }

    int choice = valid_choices[rand() % valid_count];
    free(valid_choices);
    return choice;
}

// Function to return a pair N and K that matches the reliability threshold
//~ void random_schedule(int number_of_nodes, double* reliability_of_nodes, double reliability_threshold, double* node_sizes, double file_size, int** set_of_nodes_chosen, int* N, int* K, double* updated_node_sizes) {
void random_schedule(int number_of_nodes, Node* nodes, float reliability_threshold, double size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, int closest_index, LinearModel* models, LinearModel* models_reconstruct, int nearest_size, DataList* list, int data_id, int max_N, double* total_read_time_parrallelized, double* total_read_time, double* size_stored) {
    struct timeval start, end;
    gettimeofday(&start, NULL);
    long seconds, useconds;
    srand(time(NULL));  // Seed the random number generator
    int* already_looked_at = (int*)malloc(number_of_nodes * sizeof(int));
    int already_looked_at_count = 0;
    int solution_found = 0;
    double* reliability_of_nodes_chosen;
    int* set_of_nodes_chosen;
    *N = -1;
    *K = -1;
    
    qsort(nodes, number_of_nodes, sizeof(Node), compare_nodes_by_storage_desc_with_condition);
    while (!solution_found) {
        *N = get_random_excluding_exclusions(max_N, already_looked_at, already_looked_at_count);
        if (*N == -1) {
            free(set_of_nodes_chosen);
            free(reliability_of_nodes_chosen);
            free(already_looked_at);
            gettimeofday(&end, NULL);
            seconds  = end.tv_sec  - start.tv_sec;
            useconds = end.tv_usec - start.tv_usec;
            *total_scheduling_time += seconds + useconds/1000000.0;
            return;
        }
        already_looked_at[already_looked_at_count++] = *N;

        *K = rand() % (*N - 1) + 1;
        set_of_nodes_chosen = malloc(*N * sizeof(int));
        get_random_sample(set_of_nodes_chosen, max_N, *N);
        reliability_of_nodes_chosen = (double*)malloc(*N*sizeof(double));
        reliability_of_nodes_chosen = extract_reliabilities_of_chosen_nodes(nodes, number_of_nodes, set_of_nodes_chosen, *N);
        //~ printf("2.\n"); fflush(stdout);
        int decrease_K = 0;
        while (!reliability_threshold_met_accurate(*N, *K, reliability_threshold, reliability_of_nodes_chosen)) {
            //~ printf("2.1.\n"); fflush(stdout);
            //~ if (decrease_K == max_N - 1) { break; } // TODO fix this
            //~ printf("2.2.\n"); fflush(stdout);
            *N = rand() % (max_N - 1) + 2;
            //~ printf("2.2.1. %d\n", *N - decrease_K); fflush(stdout);
            if (*N - decrease_K == 0) { *N = -1; break; } // TODO fix this
            *K = rand() % (*N - decrease_K);
            //~ printf("2.2.2.\n"); fflush(stdout);
            free(reliability_of_nodes_chosen);
            //~ printf("2.3 N%d\n", *N); fflush(stdout);
            free(set_of_nodes_chosen);
            //~ printf("2.4.\n"); fflush(stdout);
            set_of_nodes_chosen = malloc(*N * sizeof(int));
            get_random_sample(set_of_nodes_chosen, max_N, *N);
            //~ printf("2.5.\n"); fflush(stdout);
            //~ reliability_of_nodes_chosen = NULL;
            reliability_of_nodes_chosen = (double*)malloc(*N*sizeof(double));
            reliability_of_nodes_chosen = extract_reliabilities_of_chosen_nodes(nodes, number_of_nodes, set_of_nodes_chosen, *N);
            //~ printf("2.6.\n"); fflush(stdout);
            decrease_K++;
            //~ printf("2.7.\n"); fflush(stdout);
        }
        //~ printf("3.\n"); fflush(stdout);
        
        if (nodes_can_fit_new_data(set_of_nodes_chosen, *N, size / *K, nodes)) {
            solution_found = 1;
        }
    }
    // Updates
    if (*N != -1) { // We have a valid solution        
        double min_write_bandwidth = DBL_MAX;
        double min_read_bandwidth = DBL_MAX;
        
        // Writing down the results
        double total_upload_time_to_print = 0;
        
        /** Read **/
        double total_read_time_to_print = 0;
        double total_read_time_parralelized_to_print = 0;
        double reconstruct_time = 0;
        
        double chunk_size = size/(*K);
        *number_of_data_stored += 1;
        *total_N += *N;
        *total_storage_used += chunk_size*(*N);
        *size_stored += size;
        
        int* used_combinations = malloc(*N * sizeof(int));
        
        for (int j = 0; j < *N; j++) {
            total_upload_time_to_print += chunk_size/nodes[j].write_bandwidth;
            
            /** Read **/
            total_read_time_to_print += chunk_size/nodes[j].read_bandwidth;
            
            nodes[j].storage_size -= chunk_size;
            if (min_write_bandwidth > nodes[j].write_bandwidth) {
                min_write_bandwidth = nodes[j].write_bandwidth;
            }
            if (min_read_bandwidth > nodes[j].read_bandwidth) {
                min_read_bandwidth = nodes[j].read_bandwidth;
            }
            // To track the chunks I a fill a temp struct with nodes
            used_combinations[j] = nodes[j].id;
        }
        
        // Adding the chunks in the chosen nodes
        add_shared_chunks_to_nodes(used_combinations, *N, data_id, chunk_size, nodes, number_of_nodes, size);
        *total_parralelized_upload_time += chunk_size/min_write_bandwidth;
        
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
        //~ *total_read_time_parrallelized += total_read_time_parralelized_to_print;
        *total_read_time_parrallelized += fmax(size/out_going_bandwidth, total_read_time_parralelized_to_print);
        *total_read_time += total_read_time_to_print;
        free(used_combinations);
    }
    
    free(set_of_nodes_chosen);
    free(reliability_of_nodes_chosen);
    free(already_looked_at);
    
    gettimeofday(&end, NULL);
    seconds  = end.tv_sec  - start.tv_sec;
    useconds = end.tv_usec - start.tv_usec;
    *total_scheduling_time += seconds + useconds/1000000.0;
}
