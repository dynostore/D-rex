#include <stdio.h>
#include <math.h>
#include <float.h>
#include <stdlib.h>
#include <stdbool.h>
#include <../schedulers/algorithm4.h>
#include <k_means_clustering.h>

// Function to select a random node index from a cluster, ensuring uniqueness
int get_unique_random_node_index(Cluster *cluster, bool *used_nodes, int total_nodes) {
    int available_count = 0;
    int* available_nodes = malloc(cluster->num_members * sizeof(int));
    if (!available_nodes) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    // Collect indices of available nodes that are not used
    for (int i = 0; i < cluster->num_members; i++) {
        int node_index = cluster->members[i];
        if (!used_nodes[node_index]) {
            available_nodes[available_count++] = node_index;
        }
    }

    if (available_count == 0) {
        free(available_nodes);
        return -1; // No available nodes
    }

    // Select a random index from available nodes
    int random_index = rand() % available_count;
    int result = available_nodes[random_index];
    free(available_nodes);
    return result;
}

// Function to select a random node index from a cluster, ensuring uniqueness
int get_unique_random_node_index_index(Cluster *cluster, bool *used_nodes, int total_nodes) {
    int available_count = 0;
    int* available_nodes = malloc(cluster->num_members * sizeof(int));
    if (!available_nodes) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    // Collect indices of available nodes that are not used
    for (int i = 0; i < cluster->num_members; i++) {
        int node_index = i;
        if (!used_nodes[node_index]) {
            available_nodes[available_count] = node_index;
            available_count++;
        }
    }

    if (available_count == 0) {
        free(available_nodes);
        return -1; // No available nodes
    }

    // Select a random index from available nodes
    int random_index = rand() % available_count;
    int result = available_nodes[random_index];
    free(available_nodes);
    return result;
}



// Calculate Euclidean distance between a node and a cluster centroid
double euclidean_distance(Node* node, Cluster* cluster) {
    return sqrt(pow(node->storage_size - cluster->storage_size, 2) +
                pow(node->write_bandwidth - cluster->write_bandwidth, 2) +
                pow(node->read_bandwidth - cluster->read_bandwidth, 2) +
                pow(node->probability_failure - cluster->probability_failure, 2));
}

// Initialize clusters with random nodes
void initialize_clusters(Cluster* clusters, Node* nodes, int num_clusters, int num_nodes) {
    for (int i = 0; i < num_clusters; i++) {
        int index = rand() % num_nodes;
        clusters[i].storage_size = nodes[index].storage_size;
        clusters[i].write_bandwidth = nodes[index].write_bandwidth;
        clusters[i].read_bandwidth = nodes[index].read_bandwidth;
        clusters[i].probability_failure = nodes[index].probability_failure;
        clusters[i].members = (int*)malloc(num_nodes * sizeof(int));
        clusters[i].num_members = 0;
    }
}

// Assign nodes to the nearest cluster
void assign_nodes_to_clusters(Node* nodes, Cluster* clusters, int num_clusters, int num_nodes) {
    for (int i = 0; i < num_nodes; i++) {
        double min_distance = DBL_MAX;
        int cluster_index = 0;
        for (int j = 0; j < num_clusters; j++) {
            double distance = euclidean_distance(&nodes[i], &clusters[j]);
            if (distance < min_distance) {
                min_distance = distance;
                cluster_index = j;
            }
        }
        clusters[cluster_index].members[clusters[cluster_index].num_members++] = i;
    }
}

// Update cluster centroids based on assigned nodes
void update_clusters(Node* nodes, Cluster* clusters, int num_clusters) {
    for (int i = 0; i < num_clusters; i++) {
        if (clusters[i].num_members == 0) continue;

        double sum_storage_size = 0;
        double sum_write_bandwidth = 0;
        double sum_read_bandwidth = 0;
        double sum_failure_rate = 0;

        for (int j = 0; j < clusters[i].num_members; j++) {
            int node_index = clusters[i].members[j];
            sum_storage_size += nodes[node_index].storage_size;
            sum_write_bandwidth += nodes[node_index].write_bandwidth;
            sum_read_bandwidth += nodes[node_index].read_bandwidth;
            sum_failure_rate += nodes[node_index].probability_failure;
        }

        clusters[i].storage_size = sum_storage_size / clusters[i].num_members;
        clusters[i].write_bandwidth = sum_write_bandwidth / clusters[i].num_members;
        clusters[i].read_bandwidth = sum_read_bandwidth / clusters[i].num_members;
        clusters[i].probability_failure = sum_failure_rate / clusters[i].num_members;
    }
}

// K-means clustering algorithm
void k_means(Node* nodes, int num_nodes, int num_clusters, int max_iterations, Cluster* clusters) {
    initialize_clusters(clusters, nodes, num_clusters, num_nodes);

    for (int iteration = 0; iteration < max_iterations; iteration++) {
        // Reset cluster members
        for (int i = 0; i < num_clusters; i++) {
            clusters[i].num_members = 0;
        }

        // Assign nodes to the nearest cluster
        assign_nodes_to_clusters(nodes, clusters, num_clusters, num_nodes);
        // Update cluster centroids
        update_clusters(nodes, clusters, num_clusters);
    }

    // Print cluster centroids and members
    for (int i = 0; i < num_clusters; i++) {
        printf("Cluster %d:\n", i);
        printf(" Centroid: Storage Size = %.2f, Write Bandwidth = %d, Read Bandwidth = %d, Failure Rate = %.2f\n",
               clusters[i].storage_size, clusters[i].write_bandwidth,
               clusters[i].read_bandwidth, clusters[i].probability_failure);
        printf(" Members:\n");
        for (int j = 0; j < clusters[i].num_members; j++) {
            int node_index = clusters[i].members[j];
            printf("  Node %d: Storage Size = %.2f, Write Bandwidth = %d, Read Bandwidth = %d, Failure Rate = %.2f\n",
                   nodes[node_index].id, nodes[node_index].storage_size,
                   nodes[node_index].write_bandwidth, nodes[node_index].read_bandwidth,
                   nodes[node_index].probability_failure);
        }
        printf("\n");
    }
}

// Free allocated memory for clusters
void free_clusters(Cluster* clusters, int num_clusters) {
    for (int i = 0; i < num_clusters; i++) {
        free(clusters[i].members);
    }
    free(clusters);
}

// Function to calculate the binomial coefficient C(n, k)
unsigned long long binomial_coefficient(int n, int k) {
    if (k > n) return 0;
    if (k == 0 || k == n) return 1;
    if (k > n - k) k = n - k;
    
    unsigned long long result = 1;
    for (int i = 0; i < k; ++i) {
        result *= (n - i);
        result /= (i + 1);
    }
    return result;
}

// Function to calculate the number of combinations with repetition
unsigned long long combinations_with_replacement(int N, int X) {
    return binomial_coefficient(N + X - 1, X);
}

// Function to find the maximum value of N such that the sum of combinations does not exceed A
int find_max_N_for_sum(int max_X, unsigned long long A) {
    int max_N = 10000; // Set a reasonable upper bound for N
    int optimal_N = 0;
    unsigned long long total_combinations = 0;

    for (int N = 0; N <= max_N; ++N) {
        total_combinations = 0;
        for (int X = 2; X <= max_X; ++X) {
            unsigned long long combinations = combinations_with_replacement(N, X);
            total_combinations += combinations;
            if (total_combinations > A) {
                break;
            }
        }
        if (total_combinations <= A) {
            optimal_N = N;
        } else {
            break;
        }
    }
    if (optimal_N == 0) {
        printf("Error provided max number of combinations is too high\n");
    }

    return optimal_N;
}
