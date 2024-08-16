#ifndef COMBINATIONS_H
#define COMBINATIONS_H

//~ void create_combinations_from_one_cluster(Cluster *cluster, int r, Node *nodes, Combination **combinations, int *combination_count);
//~ void create_combinations_from_clusters(Cluster *clusters, int num_clusters, int r, Node *nodes, Combination **combinations, int *combination_count);
void create_combinations_with_limit(Node *nodes, int n, int r, Combination **combinations, int *combination_count, int limit);
void create_combinations(Node *nodes, int n, int r, Combination **combinations, int *combination_count);
void free_combinations(Combination **combinations, int count);

#endif

