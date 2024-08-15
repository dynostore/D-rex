#ifndef COMBINATIONS_H
#define COMBINATIONS_H

void create_combinations_from_one_cluster(Cluster *cluster, int r, Node *nodes, Combination **combinations, int *combination_count);
void create_combinations_from_clusters(Cluster *clusters, int num_clusters, int r, Node *nodes, Combination **combinations, int *combination_count);

#endif

