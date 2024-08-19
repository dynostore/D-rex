#include <stdio.h>
#include <math.h>
#include <float.h>
#include <stdlib.h>
#include <stdbool.h>
#include <../schedulers/algorithm4.h>
#include <../utils/k_means_clustering.h>
#include <../schedulers/bogdan_balance_penalty.h>

double get_avg_free_storage (int number_of_nodes, Node* nodes) {
    double total_free_storage = 0;
    for (int i = 0; i < number_of_nodes; i++) {
        total_free_storage += nodes[i]->storage_size;
    }
    return total_free_storage/number_of_nodes;
}

/**
 * for (D = 1; D < N; D++) {
    balance_penalty = 0;
    for (j = 0; j < D; j++)
        if (free_capacity[D] < S/(D + P))
            continue;
        balance_penalty += abs(free_capacity[D] - S/(D + P) - avg_free_capacity);
    for (j = D; j < N; j++)
        balance_penalty += abs(free_capacity[D] - avg_free_capacity);
    if balance_penalty < min_balance_penalty) {
        min_D = D;
        min_balance_penalty = balance_penalty;
    }
   }
 * D for data chunks and P for parity chunks and (D+P)*chunk_size = total_size and S for data size
 * Then you maximize D so you can minimize P * chunk_size
 * A simple naive strategy is to maximize D and choose P as small as possible to achieve the same resilience as your algo, for example, you start with P=1 and you keep increasing P until you are equivalent (in terms of resilience) to your strategy
 **/
//~ void balance_penalty_algorithm (int number_of_nodes, Node* nodes, float reliability_threshold, double size, double max_node_size, double min_data_size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, Combination **combinations, int total_combinations, double* total_remaining_size, double total_storage_size, int closest_index, RealRecords* records_array, LinearModel* models, int nearest_size, DataList* list, int data_id) {
void balance_penalty_algorithm (int number_of_nodes, Node* nodes, float reliability_threshold, double S, int *N, int *K) {
    double balance_penalty;
    double min_balance_penalty = DBL_MAX;
    int D;
    int min_D;
    int j;
    int P = 1;
    double avg_free_capacity = get_avg_free_storage(number_of_nodes, nodes);
    printf("avg_free_capacity = %f\n", avg_free_capacity);
    
    for (D = 1; D < number_of_nodes; D++) {
        balance_penalty = 0;
        for (j = 0; j < D; j++) {
            if (nodes[j]->storage_size < S/(D + P))
            {
                continue;
            }
            balance_penalty += fabs(nodes[j]->storage_size - S/(D + P) - avg_free_capacity);
        }
        
        for (j = D; j < N; j++) {
            printf("+= %f in second for loop\n", fabs(nodes[j]->storage_size - avg_free_capacity));
            balance_penalty += fabs(nodes[j]->storage_size - avg_free_capacity);
        }
        
        if (balance_penalty < min_balance_penalty) {
            printf("New min_D %f with %d\n", min_balance_penalty, D);
            min_D = D;
            min_balance_penalty = balance_penalty;
        }
    }
    
    // I guess that I need to fetch the nodes associated with min_D and extract N and K
    
    // TODO: update node sizes like in alg4 and write results in a file
}
