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
            perror("Node index out of bounds");
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
void random_schedule(int number_of_nodes, Node* nodes, float reliability_threshold, double size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, int closest_index, LinearModel* models, int nearest_size, DataList* list, int data_id) {
    struct timeval start, end;
    gettimeofday(&start, NULL);
    long seconds, useconds;
    int i;
    srand(time(NULL));  // Seed the random number generator
    //~ printf("Data %d\n", data_id + 1);
    int* already_looked_at = (int*)malloc(number_of_nodes * sizeof(int));
    int already_looked_at_count = 0;
    int solution_found = 0;
    double* reliability_of_nodes_chosen;
    int* set_of_nodes_chosen;
    *N = -1;
    *K = -1;
    
    qsort(nodes, number_of_nodes, sizeof(Node), compare_nodes_by_storage_desc_with_condition);
    
    while (!solution_found) {
        *N = get_random_excluding_exclusions(number_of_nodes, already_looked_at, already_looked_at_count);
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
        //~ printf("N %d K %d\n", *N, *K);  
        get_random_sample(set_of_nodes_chosen, number_of_nodes, *N);
        reliability_of_nodes_chosen = extract_reliabilities_of_chosen_nodes(nodes, number_of_nodes, set_of_nodes_chosen, *N);

        //~ printf("Selected nodes: ");
        //~ for (i = 0; i < *N; i++) {
            //~ printf("%d ", set_of_nodes_chosen[i]);
            //~ printf("%f ", reliability_of_nodes_chosen[i]);
        //~ }
        //~ printf("\n");
        //~ exit(1);
        // Sort nodes (using a simple sort, or implement a better sorting algorithm)
        //~ qsort(*set_of_nodes_chosen, *N, sizeof(int), (int(*)(const void*, const void*)) strcmp);

        //~ double* reliability_of_nodes = extract_first_X_reliabilities(nodes, number_of_nodes, *N);
        //~ return reliability_threshold_met_accurate(D + P, D, reliability_threshold, reliability_of_nodes);
    
        //~ if (reliability_of_nodes_chosen == NULL) {
            //~ perror("Failed to allocate memory for reliability_of_nodes_chosen");
            //~ free(already_looked_at);
            //~ free(*set_of_nodes_chosen);
            //~ return;
        //~ }

        //~ for (int i = 0; i < *N; i++) {
            //~ reliability_of_nodes_chosen[i] = reliability_of_nodes[(*set_of_nodes_chosen)[i]];
        //~ }

        while (!reliability_threshold_met_accurate(*N, *K, reliability_threshold, reliability_of_nodes_chosen)) {
            *N = rand() % (number_of_nodes - 1) + 2;
            *K = rand() % (*N - 1) + 1;
            free(reliability_of_nodes_chosen);
            free(set_of_nodes_chosen);
            get_random_sample(set_of_nodes_chosen, number_of_nodes, *N);
            reliability_of_nodes_chosen = extract_reliabilities_of_chosen_nodes(nodes, number_of_nodes, set_of_nodes_chosen, *N);
            //~ printf("Reliability not met, chose new N and K %d %d\n", *N, *K);
        }
        
        if (nodes_can_fit_new_data(set_of_nodes_chosen, *N, size / *K, nodes)) {
            solution_found = 1;
            //~ printf("Can fit!\n");
        }
    }
    
    // Updates
    if (*N != -1) { // We have a valid solution        
        double min_write_bandwidth = DBL_MAX;
        
        // Writing down the results
        double total_upload_time_to_print = 0;
        double chunk_size = size/(*K);
        *number_of_data_stored += 1;
        *total_N += *N;
        *total_storage_used += chunk_size*(*N);
        Node** used_combinations = malloc(*N * sizeof(Node*));
        
        for (int j = 0; j < *N; j++) {
            total_upload_time_to_print += chunk_size/nodes[j].write_bandwidth;
            nodes[j].storage_size -= chunk_size;
            if (min_write_bandwidth > nodes[j].write_bandwidth) {
                min_write_bandwidth = nodes[j].write_bandwidth;
            }
            // To track the chunks I a fill a temp struct with nodes
            used_combinations[j] = &nodes[j];
        }
        
        // Adding the chunks in the chosen nodes
        add_shared_chunks_to_nodes(used_combinations, *N, data_id);
        *total_parralelized_upload_time += chunk_size/min_write_bandwidth;
        
        // TODO: remove this 3 lines under to reduce complexity if we don't need the trace per data
        double chunking_time = predict(models[closest_index], *N, *K, nearest_size, size);
        double transfer_time_parralelized = calculate_transfer_time(chunk_size, min_write_bandwidth);
        add_node_to_print(list, data_id, size, total_upload_time_to_print, transfer_time_parralelized, chunking_time, *N, *K);
        *total_upload_time += total_upload_time_to_print;
    }
    
    free(set_of_nodes_chosen);
    free(reliability_of_nodes_chosen);
    free(already_looked_at);
    
    gettimeofday(&end, NULL);
    seconds  = end.tv_sec  - start.tv_sec;
    useconds = end.tv_usec - start.tv_usec;
    *total_scheduling_time += seconds + useconds/1000000.0;
}
