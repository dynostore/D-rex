#ifndef BOGDAN_BALANCE_PENALTY_H
#define BOGDAN_BALANCE_PENALTY_H

#include "../utils/prediction.h"

double* extract_first_X_reliabilities(Node* nodes, int total_nodes, int X);
double get_avg_free_storage (int number_of_nodes, Node* nodes);
void balance_penalty_algorithm (int number_of_nodes, Node* nodes, float reliability_threshold, double S, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, double* total_remaining_size, int closest_index, LinearModel* models, LinearModel* models_reconstruct, int nearest_size, DataList* list, int data_id, int max_N, double* total_read_time_parrallelized, double* total_read_time, double* size_stored);

#endif
