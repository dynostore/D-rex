#ifndef ALG4_H
#define ALG4_H

typedef struct {
    int id;
    double storage_size;
    int write_bandwidth;
    int read_bandwidth;
    double probability_failure;
    int add_after_x_jobs;  // Number of jobs after which the node becomes available
} Node;

typedef struct data_to_print {
    int id;
    double size;
    double total_transfer_time;
    double transfer_time_parralelized;
    double chunking_time;
    int N;
    int K;
    struct data_to_print *next;
} DataToPrint;

typedef struct {
    DataToPrint *head;
    DataToPrint *tail;
} DataList;

typedef struct {
    int num_elements; // Number of nodes in the combination
    Node** nodes; // Array of pointers to Node structs
    double* probability_failure; // Array of reliability
    double variance_reliability; // To avoid having to compute it all the time
    double sum_reliability; // To avoid having to compute it all the time
    int* write_bandwidth; // Array of bandwidths
    double min_remaining_size; // Smallest node's remaining memory in the combination. Used to quickly skip an unvalid combination
    int min_write_bandwidth; // Smallest node's write bandwidth in the combination
    
    // Sub values for pareto front
    double transfer_time_parralelized;
    double total_transfer_time;
    double chunking_time;
    
    // Values in the pareto front
    double size_score;
    double replication_and_write_time;
    double storage_overhead;
    int K;
} Combination;

#endif

