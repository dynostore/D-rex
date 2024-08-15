#ifndef KMEANS_H
#define KMEANS_H

typedef struct {
    double storage_size;
    int write_bandwidth;
    int read_bandwidth;
    double probability_failure;
    int* members;        // Array of indices of nodes belonging to this cluster
    int num_members;
} Cluster;

int get_unique_random_node_index(Cluster *cluster, bool *used_nodes, int total_nodes);
int get_unique_random_node_index_index(Cluster *cluster, bool *used_nodes, int total_nodes);
unsigned long long binomial_coefficient(int n, int k);
unsigned long long combinations_with_replacement(int N, int X);
int find_max_N_for_sum(int max_X, unsigned long long A);
double euclidean_distance(Node* node, Cluster* cluster);
void initialize_clusters(Cluster* clusters, Node* nodes, int num_clusters, int num_nodes);
// Assign nodes to the nearest cluster
void assign_nodes_to_clusters(Node* nodes, Cluster* clusters, int num_clusters, int num_nodes);
// Update cluster centroids based on assigned nodes
void update_clusters(Node* nodes, Cluster* clusters, int num_clusters);
// K-means clustering algorithm
void k_means(Node* nodes, int num_nodes, int num_clusters, int max_iterations, Cluster* clusters);
void free_clusters(Cluster* clusters, int num_clusters);

#endif

