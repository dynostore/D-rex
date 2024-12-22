#include <stdio.h>
#include <math.h>
#include <float.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <stdbool.h>
#include <../schedulers/algorithm4.h>
#include <k_means_clustering.h>
#include <combinations.h>

void free_combinations(Combination** combinations, int num_combinations) {
    //~ printf("1.\n"); fflush(stdout);
    for (int i = 0; i < num_combinations; i++) {
        if (combinations[i] != NULL) {
            // Free the array of Node pointers (if dynamically allocated)
            if (combinations[i]->nodes != NULL) {
                free(combinations[i]->nodes);
            }

            // Free the array of probability_failure
            if (combinations[i]->probability_failure != NULL) {
                free(combinations[i]->probability_failure);
            }

            // Free the array of write_bandwidth
            if (combinations[i]->write_bandwidth != NULL) {
                free(combinations[i]->write_bandwidth);
            }

            // Free the Combination struct itself
            free(combinations[i]);
        }
    }

    // Finally, free the array of Combination* pointers
    free(combinations);
    //~ printf("2.\n"); fflush(stdout);
}

void create_combinations(Node *nodes, int n, int r, Combination **combinations, int *combination_count) {
    int *indices = malloc(r * sizeof(int));
    if (!indices) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    
    //~ printf("r %d\n", r);
    
    for (int i = 0; i < r; i++) {
        indices[i] = i;
    }

    while (1) {
        combinations[*combination_count] = malloc(sizeof(Combination));
        combinations[*combination_count]->num_elements = r;
        combinations[*combination_count]->nodes = malloc(r * sizeof(Node*));
        combinations[*combination_count]->probability_failure = malloc(r * sizeof(double));
        combinations[*combination_count]->sum_reliability = 0;
        combinations[*combination_count]->variance_reliability = 0;
        combinations[*combination_count]->write_bandwidth = malloc(r * sizeof(int));
        //~ combinations[*combination_count]->min_remaining_size = DBL_MAX;
        combinations[*combination_count]->min_write_bandwidth = INT_MAX;
        combinations[*combination_count]->min_read_bandwidth = INT_MAX;

        for (int i = 0; i < r; i++) {
            combinations[*combination_count]->nodes[i] = &nodes[indices[i]];
            combinations[*combination_count]->probability_failure[i] = nodes[indices[i]].probability_failure;
            combinations[*combination_count]->sum_reliability += nodes[indices[i]].probability_failure;
            combinations[*combination_count]->variance_reliability += nodes[indices[i]].probability_failure * (1 - nodes[indices[i]].probability_failure);
            combinations[*combination_count]->write_bandwidth[i] = nodes[indices[i]].write_bandwidth;
            //~ printf("Adding %d\n", nodes[indices[i]].write_bandwidth);
            //~ if (nodes[indices[i]].storage_size < combinations[*combination_count]->min_remaining_size) {
                //~ combinations[*combination_count]->min_remaining_size = nodes[indices[i]].storage_size;
            //~ }
            if (nodes[indices[i]].write_bandwidth < combinations[*combination_count]->min_write_bandwidth) {
                combinations[*combination_count]->min_write_bandwidth = nodes[indices[i]].write_bandwidth;
            }
            if (nodes[indices[i]].read_bandwidth < combinations[*combination_count]->min_read_bandwidth) {
                combinations[*combination_count]->min_read_bandwidth = nodes[indices[i]].read_bandwidth;
            }
        }
        (*combination_count)++;
        
        int i = r - 1;
        
        while (i >= 0 && indices[i] == n - r + i) {
            i--;
        }

        if (i < 0) {
            break;
        }

        indices[i]++;

        for (int j = i + 1; j < r; j++) {
            indices[j] = indices[j - 1] + 1;
        }
    }
    free(indices);
}

void create_combinations_with_limit(Node *nodes, int n, int r, Combination **combinations, int *combination_count, int limit) {
    int *indices = malloc(r * sizeof(int));
    if (!indices) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    for (int i = 0; i < r; i++) {
        indices[i] = i;
    }

    while (limit != 0) {
        limit--;
        
        combinations[*combination_count] = malloc(sizeof(Combination));
        combinations[*combination_count]->num_elements = r;
        //~ printf("%d %d\n", *combination_count, combinations[*combination_count]->num_elements);
        combinations[*combination_count]->nodes = malloc(r * sizeof(Node*));
        combinations[*combination_count]->probability_failure = malloc(r * sizeof(double));
        combinations[*combination_count]->sum_reliability = 0;
        combinations[*combination_count]->variance_reliability = 0;
        combinations[*combination_count]->write_bandwidth = malloc(r * sizeof(int));
        //~ combinations[*combination_count]->min_remaining_size = DBL_MAX;
        combinations[*combination_count]->min_write_bandwidth = INT_MAX;
        combinations[*combination_count]->min_read_bandwidth = INT_MAX;

        for (int i = 0; i < r; i++) {
            combinations[*combination_count]->nodes[i] = &nodes[indices[i]];
            combinations[*combination_count]->probability_failure[i] = nodes[indices[i]].probability_failure;
            combinations[*combination_count]->sum_reliability += nodes[indices[i]].probability_failure;
            combinations[*combination_count]->variance_reliability += nodes[indices[i]].probability_failure * (1 - nodes[indices[i]].probability_failure);
            combinations[*combination_count]->write_bandwidth[i] = nodes[indices[i]].write_bandwidth;
            //~ if (nodes[indices[i]].storage_size < combinations[*combination_count]->min_remaining_size) {
                //~ combinations[*combination_count]->min_remaining_size = nodes[indices[i]].storage_size;
            //~ }
            if (nodes[indices[i]].write_bandwidth < combinations[*combination_count]->min_write_bandwidth) {
                combinations[*combination_count]->min_write_bandwidth = nodes[indices[i]].write_bandwidth;
            }
            if (nodes[indices[i]].read_bandwidth < combinations[*combination_count]->min_read_bandwidth) {
                combinations[*combination_count]->min_read_bandwidth = nodes[indices[i]].read_bandwidth;
            }
        }
        (*combination_count)++;
        
        int i = r - 1;
        
        while (i >= 0 && indices[i] == n - r + i) {
            i--;
        }

        if (i < 0) {
            break;
        }

        indices[i]++;

        for (int j = i + 1; j < r; j++) {
            indices[j] = indices[j - 1] + 1;
        }
    }
    free(indices);
}

// Function to calculate binomial coefficient
//~ unsigned long long combination(int n, int r) {
    //~ if (r > n || r < 0) return 0;
    //~ printf("%d choose %d: %lld\n", n, r, factorial(n) / (factorial(r) * factorial(n - r)));
    //~ return factorial(n) / (factorial(r) * factorial(n - r));
//~ }
// Function to compute combination C(n, r) and compare it to a threshold
unsigned long long combination(int n, int r, unsigned long long complexity_threshold) {
    if (r > n || r < 0) return 0; // Invalid case
    if (r == 0 || r == n) return 1; // Base cases
    
    // Take advantage of symmetry: C(n, r) == C(n, n-r)
    if (r > n - r) r = n - r;
    
    unsigned long long result = 1;
    for (int i = 0; i < r; ++i) {
        result *= (n - i);
        
        // To prevent overflow, we check if the result is still below the threshold
        if (result > complexity_threshold * (i + 1)) {
            return complexity_threshold; // Return threshold if overflow will occur
        }
        
        result /= (i + 1);
    }
    
    return result;
}

Combination** reset_combinations_and_recreate_them(int* total_combinations, int min_number_node_in_combination, int current_number_of_nodes, int complexity_threshold, Node* nodes, int i, bool* reduced_complexity_situation)
{
    int j = 0;
    Combination** combinations = NULL;

    // Free old combinations
    //~ printf("free %d combinations\n", *total_combinations);
    //~ free_combinations(combinations, *total_combinations);
    
    *total_combinations = 0;

    int max_number_node_in_combination = current_number_of_nodes;
    for (j = min_number_node_in_combination; j <= max_number_node_in_combination; j++) {
        *total_combinations += combination(current_number_of_nodes, j, complexity_threshold);
    }
    int combination_count = 0;

    if (*total_combinations >= complexity_threshold) {
        *reduced_complexity_situation = true;
        //~ printf("sorted version complexity_threshold = %d\n", complexity_threshold);
        //~ global_current_data_value = i;
        //~ printf("global_current_data_value after = %d\n", global_current_data_value);
        int max_number_combination_per_r = complexity_threshold/(current_number_of_nodes - 1);
        qsort(nodes, current_number_of_nodes, sizeof(Node), compare_nodes_by_storage_desc_with_condition);
        //~ print_nodes(nodes, current_number_of_nodes);
        
        combinations = NULL;
        combinations = malloc(complexity_threshold * sizeof(Combination *));
        
        for (j = min_number_node_in_combination; j <= max_number_node_in_combination; j++) {
            //~ printf("Create\n");
            create_combinations_with_limit(nodes, current_number_of_nodes, j, combinations, &combination_count, max_number_combination_per_r);
        }
        *total_combinations = combination_count;
        //~ printf("*total_combinations after %d\n", *total_combinations);
    }
    else {
        *reduced_complexity_situation = false;
        combinations = malloc(*total_combinations * sizeof(Combination *));
        if (combinations == NULL) {
            perror("Error allocating memory for combinations");
            exit(EXIT_FAILURE);
        }
        for (j = min_number_node_in_combination; j <= max_number_node_in_combination; j++) {
            create_combinations(nodes, current_number_of_nodes, j, combinations, &combination_count);
        }
    }
    return combinations;
}
