#include <stdio.h>
#include <math.h>
#include <float.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <stdbool.h>
#include <../schedulers/algorithm4.h>
#include <k_means_clustering.h>


// Function to create one random combination from a given cluster
void create_combinations_from_one_cluster(Cluster *cluster, int r, Node *nodes, Combination **combinations, int *combination_count) {
    if (r > cluster->num_members) {
        printf("Cannot create combination: not enough nodes in the cluster.\n");
        return;
    }

    // Allocate memory for the combination
    combinations[*combination_count] = malloc(sizeof(Combination));
    combinations[*combination_count]->num_elements = r;
    combinations[*combination_count]->nodes = malloc(r * sizeof(Node*));
    combinations[*combination_count]->probability_failure = malloc(r * sizeof(double));
    combinations[*combination_count]->sum_reliability = 0;
    combinations[*combination_count]->variance_reliability = 0;
    combinations[*combination_count]->write_bandwidth = malloc(r * sizeof(int));
    combinations[*combination_count]->min_remaining_size = DBL_MAX;
    combinations[*combination_count]->min_write_bandwidth = INT_MAX;

    // Array to keep track of used indices
    bool *used = malloc(cluster->num_members* sizeof(bool));
    if (!used) {
        perror("calloc");
        exit(EXIT_FAILURE);
    }

    // Generate random unique indices for the combination
    int *indices = malloc(r * sizeof(int));
    if (!indices) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    for (int i =0; i < cluster->num_members; i++) {
        used[i] = false;
    }
    //~ node_index = get_unique_random_node_index(cluster, used, -1);
    int count = 0;
    for (count = 0; count < r; count++) {
        int index = get_unique_random_node_index_index(cluster, used, -1);
        //~ if (!used[index]) {
            used[index] = true;
            indices[count] = index;
            //~ count++;
        //~ }
    }
    //~ printf("1\n");
    for (count = 0; count < r; count++) {
        printf("%d\n", indices[count]); }

    // Populate the combination
    for (int i = 0; i < r; i++) {
        int node_index = indices[i];
        //~ printf("%d\n", node_index);
        combinations[*combination_count]->nodes[i] = &nodes[cluster->members[node_index]];
        combinations[*combination_count]->probability_failure[i] = nodes[cluster->members[node_index]].probability_failure;
        combinations[*combination_count]->sum_reliability += nodes[cluster->members[node_index]].probability_failure;
        combinations[*combination_count]->variance_reliability += nodes[cluster->members[node_index]].probability_failure * (1 - nodes[cluster->members[node_index]].probability_failure);
        combinations[*combination_count]->write_bandwidth[i] = nodes[cluster->members[node_index]].write_bandwidth;
        if (nodes[cluster->members[node_index]].storage_size < combinations[*combination_count]->min_remaining_size) {
            combinations[*combination_count]->min_remaining_size = nodes[cluster->members[node_index]].storage_size;
        }
        if (nodes[cluster->members[node_index]].write_bandwidth < combinations[*combination_count]->min_write_bandwidth) {
            combinations[*combination_count]->min_write_bandwidth = nodes[cluster->members[node_index]].write_bandwidth;
        }
    }

    (*combination_count)++;

    // Print the combination
    printf("Combination from one cluster only %d:\n", *combination_count);
    for (int i = 0; i < r; i++) {
        printf("  Node %d: Storage Size = %.2f, Write Bandwidth = %d, Failure Rate = %.2f\n",
               cluster->members[indices[i]],
               nodes[cluster->members[indices[i]]].storage_size,
               nodes[cluster->members[indices[i]]].write_bandwidth,
               nodes[cluster->members[indices[i]]].probability_failure);
    }

    // Free allocated memory
    free(indices);
    //~ free(used);
}

/*
 * In order to reduce complexity of algorithm4.
 * Does not look at all the combinations because too computational intensive. The breaking point being above 10 nodes.
 * First we want to look at at most at 2000 combinations.
 * So we look at the max number of clusters we can build and build this number of kmeans cluster and generate the combinations with these clusters (repetition within a cluster is possible)
 */
 // Function to create combinations using nodes from clusters
void create_combinations_from_clusters(Cluster *clusters, int num_clusters, int r, Node *nodes, Combination **combinations, int *combination_count) {
    
        // Loop over each cluster to create combinations with nodes from a single cluster
    for (int i = 0; i < num_clusters; i++) {
        if (clusters[i].num_members >= r) {
            create_combinations_from_one_cluster(&clusters[i], r, nodes, combinations, combination_count);
        }
    }
    
    int *cluster_indices = malloc(r * sizeof(int));
    if (!cluster_indices) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    bool *used_nodes = calloc(num_clusters * r, sizeof(bool));
    if (!used_nodes) {
        perror("calloc");
        exit(EXIT_FAILURE);
    }
    
    // Initialize cluster indices
    for (int i = 0; i < r; i++) {
        cluster_indices[i] = i % num_clusters;
    }
    
    printf("r = %d\n", r);

    while (1) {
        // Create a new combination
        combinations[*combination_count] = malloc(sizeof(Combination));
        combinations[*combination_count]->num_elements = r;
        combinations[*combination_count]->nodes = malloc(r * sizeof(Node*));
        combinations[*combination_count]->probability_failure = malloc(r * sizeof(double));
        combinations[*combination_count]->sum_reliability = 0;
        combinations[*combination_count]->variance_reliability = 0;
        combinations[*combination_count]->write_bandwidth = malloc(r * sizeof(int));
        combinations[*combination_count]->min_remaining_size = DBL_MAX;
        combinations[*combination_count]->min_write_bandwidth = INT_MAX;

        // Track used nodes to ensure uniqueness
        memset(used_nodes, 0, num_clusters * r * sizeof(bool));

        // Populate the combination
        bool valid_combination = true;
        for (int i = 0; i < r; i++) {
            int cluster_index = cluster_indices[i];
            int node_index = get_unique_random_node_index(&clusters[cluster_index], used_nodes, num_clusters * r);
            if (node_index == -1) {
                valid_combination = false;
                break;
            }

            // Mark this node as used
            used_nodes[node_index] = true;

            combinations[*combination_count]->nodes[i] = &nodes[node_index];
            combinations[*combination_count]->probability_failure[i] = nodes[node_index].probability_failure;
            combinations[*combination_count]->sum_reliability += nodes[node_index].probability_failure;
            combinations[*combination_count]->variance_reliability += nodes[node_index].probability_failure * (1 - nodes[node_index].probability_failure);
            combinations[*combination_count]->write_bandwidth[i] = nodes[node_index].write_bandwidth;
            if (nodes[node_index].storage_size < combinations[*combination_count]->min_remaining_size) {
                combinations[*combination_count]->min_remaining_size = nodes[node_index].storage_size;
            }
            if (nodes[node_index].write_bandwidth < combinations[*combination_count]->min_write_bandwidth) {
                combinations[*combination_count]->min_write_bandwidth = nodes[node_index].write_bandwidth;
            }
        }

        //~ free(used_nodes)
        if (valid_combination) {
            (*combination_count)++;
        } else {
            // Free the invalid combination
            free(combinations[*combination_count]->nodes);
            free(combinations[*combination_count]->probability_failure);
            free(combinations[*combination_count]->write_bandwidth);
            free(combinations[*combination_count]);
        }

        // Find the next combination
        int i = r - 1;
        while (i >= 0 && cluster_indices[i] == num_clusters - 1) {
            i--;
        }
        if (i < 0) {
            break;
        }

        cluster_indices[i]++;
        for (int j = i + 1; j < r; j++) {
            cluster_indices[j] = cluster_indices[j - 1];
        }
        //~ free(used_nodes);
    }

    free(cluster_indices);
    free(used_nodes);
}
