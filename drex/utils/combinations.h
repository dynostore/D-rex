#ifndef COMBINATIONS_H
#define COMBINATIONS_H

//~ void create_combinations_from_one_cluster(Cluster *cluster, int r, Node *nodes, Combination **combinations, int *combination_count);
//~ void create_combinations_from_clusters(Cluster *clusters, int num_clusters, int r, Node *nodes, Combination **combinations, int *combination_count);
void create_combinations_with_limit(Node *nodes, int n, int r, Combination **combinations, int *combination_count, int limit);
void create_combinations(Node *nodes, int n, int r, Combination **combinations, int *combination_count);
void free_combinations(Combination **combinations, int count);
Combination** reset_combinations_and_recreate_them(int* total_combinations, int min_number_node_in_combination, int current_number_of_nodes, int complexity_threshold, Node* nodes, int i, bool* reduced_complexity_situation);
unsigned long long combination(int n, int r, unsigned long long complexity_threshold);

#endif

