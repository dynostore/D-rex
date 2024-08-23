#ifndef ALG4_H
#define ALG4_H

// Struct representing a chunk of data
typedef struct chunk {
    int chunk_id;           // ID of the chunk
    double chunk_size;
    int num_of_nodes_used;  // Number of nodes used to store this chunk
    int* nodes_used;        // Array of node IDs holding this chunk
    struct chunk* next;     // Pointer to the next chunk in the list
} Chunk;

// Struct representing the linked list of chunks
typedef struct {
    Chunk* head;  // Pointer to the first chunk in the list
} ChunkList;

typedef struct {
    double *probabilities;
    int n;
} PoiBin;

extern int global_current_data_value;

typedef struct {
    int id;
    double storage_size;
    int write_bandwidth;
    int read_bandwidth;
    double probability_failure;
    double daily_failure_rate;
    int add_after_x_jobs;   // Number of jobs after which the node becomes available
    ChunkList *chunks;       // Linked list of chunks stored in this node
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

int compare_nodes_by_storage_desc_with_condition(const void *a, const void *b);
void add_node_to_print(DataList *list, int id, double size, double total_transfer_time, double transfer_time_parralelized, double chunking_time, int N, int K);
void print_nodes(Node *nodes, int num_nodes);
int reliability_threshold_met_accurate(int N, int K, double reliability_threshold, double *reliability_of_nodes);
void add_shared_chunks_to_nodes(Node** nodes_used, int num_of_nodes_used, int chunk_id, double chunk_size);
int compare_nodes_by_bandwidth_desc_with_condition(const void *a, const void *b);
int get_max_K_from_reliability_threshold_and_nodes_chosen(int number_of_nodes, float reliability_threshold, double sum_reliability, double variance_reliability, double* reliability_of_nodes);
void add_shared_chunks_to_nodes_3_replication(Node** nodes_used, int num_of_nodes_used, int chunk_id, double* size_to_stores);

#endif


