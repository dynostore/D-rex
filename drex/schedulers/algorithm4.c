#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <limits.h>
#include <math.h>
#include <stdbool.h>
#include <string.h>
#include "../utils/prediction.h"
#include "../utils/pareto_knee.h"
#include <sys/time.h>

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
    int id;
    double storage_size;
    int write_bandwidth;
    int read_bandwidth;
    double probability_failure;
    int add_after_x_jobs;  // Number of jobs after which the node becomes available
} Node;

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

DataToPrint* create_node(int id, double size, double total_transfer_time, double transfer_time_parralelized, double chunking_time, int N, int K) {
    DataToPrint *new_node = (DataToPrint*)malloc(sizeof(DataToPrint));
    if (!new_node) {
        perror("Failed to allocate memory for new node");
        exit(EXIT_FAILURE);
    }
    new_node->id = id;
    new_node->size = size;
    new_node->total_transfer_time = total_transfer_time;
    new_node->transfer_time_parralelized = transfer_time_parralelized;
    new_node->chunking_time = chunking_time;
    new_node->N = N;
    new_node->K = K;
    new_node->next = NULL;
    return new_node;
}

void init_list(DataList *list) {
    list->head = NULL;
    list->tail = NULL;
}

void add_node_to_print(DataList *list, int id, double size, double total_transfer_time, double transfer_time_parralelized, double chunking_time, int N, int K) {
    DataToPrint *new_node = create_node(id, size, total_transfer_time, transfer_time_parralelized, chunking_time, N, K);
    if (list->tail) {
        list->tail->next = new_node;
    } else {
        list->head = new_node;
    }
    list->tail = new_node;
}

void write_linked_list_to_file(DataList *list, const char *filename, double* total_chunking_time) {
    FILE *file = fopen(filename, "w");
    if (!file) {
        perror("Failed to open file");
        exit(EXIT_FAILURE);
    }
    
    fprintf(file, "ID, Size, Total Transfer Time, Transfer Time Parralelized, Chunking Time, N, K\n");
    DataToPrint *current = list->head;
    while (current) {
        fprintf(file, "%d, %f, %f, %f, %f, %d, %d\n", current->id, current->size, current->total_transfer_time, current->transfer_time_parralelized, current->chunking_time, current->N, current->K);
        *total_chunking_time += current->chunking_time;
        current = current->next;
    }
    fclose(file);
}

// Function to count the number of nodes in the file
int count_nodes(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }

    // Count lines to determine the number of nodes
    int count = 0;
    char line[256];  // Adjust size if needed

    while (fgets(line, sizeof(line), file)) {
        count++;
    }

    fclose(file);

    // Subtract 1 if the first line is a header
    return count - 1;  // Adjust if there is no header
}

// Function to count the number of lines with Access Type 2
int count_lines_with_access_type(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }

    // Read the header line
    char header[256];
    if (fgets(header, sizeof(header), file) == NULL) {
        perror("Error reading header");
        fclose(file);
        exit(EXIT_FAILURE);
    }

    int count = 0;
    int temp_access_type;
    char line[256];

    while (fgets(line, sizeof(line), file)) {
        // Parse the line
        if (sscanf(line, "%*d,%*f,%*f,%*f,%d", &temp_access_type) == 1) {
            if (temp_access_type == 2) {
                count++;
            }
        } else {
            fprintf(stderr, "Error parsing line: %s\n", line);
        }
    }

    fclose(file);
    return count;
}

// Function to calculate the probability of failure over a given period given the annual failure rate
double probability_of_failure(double failure_rate, double data_duration_on_system) {
    // Convert data duration to years
    double data_duration_in_years = data_duration_on_system / 365.0;
    
    // Convert failure rate to a fraction
    double lambda_rate = failure_rate / 100.0;
    
    // Calculate the probability of failure
    double probability_failure = 1 - exp(-lambda_rate * data_duration_in_years);
    
    return probability_failure;
}

// Function to read data from file and populate the nodes array
void read_node(const char *filename, int number_of_nodes, Node *nodes, double data_duration_on_system, double* max_node_size, double* total_storage_size, double* initial_node_sizes) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }

    // Skip the header line if present
    char line[256];
    fgets(line, sizeof(line), file);

    // Read the file line by line and populate nodes array
    int index = 0;
    while (fscanf(file, "%d,%lf,%d,%d,%lf",
                  &nodes[index].id,
                  &nodes[index].storage_size,
                  &nodes[index].write_bandwidth,
                  &nodes[index].read_bandwidth,
                  &nodes[index].probability_failure) == 5) {
        nodes[index].add_after_x_jobs = 0;
        if (nodes[index].storage_size > *max_node_size)
        {
            *max_node_size = nodes[index].storage_size;
        }
        *total_storage_size += nodes[index].storage_size;
        initial_node_sizes[index] = nodes[index].storage_size;
        index++;
    }
    // Update the annual failure rate to become the probability of failure of the node
    for (int i = 0; i < number_of_nodes; i++) {
        nodes[i].probability_failure = probability_of_failure(nodes[i].probability_failure, data_duration_on_system);
    }

    fclose(file);
}

void read_supplementary_node(const char *filename, int number_of_nodes, Node *nodes, double data_duration_on_system, double* max_node_size, double* total_storage_size, double* initial_node_sizes, int previous_number_of_nodes) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }

    // Skip the header line if present
    char line[256];
    fgets(line, sizeof(line), file);

    // Read the file line by line and populate nodes array
    int index = 0;
    while (fscanf(file, "%d,%lf,%d,%d,%lf,%d",
                  &nodes[previous_number_of_nodes + index].id,
                  &nodes[previous_number_of_nodes + index].storage_size,
                  &nodes[previous_number_of_nodes + index].write_bandwidth,
                  &nodes[previous_number_of_nodes + index].read_bandwidth,
                  &nodes[previous_number_of_nodes + index].probability_failure,
                  &nodes[previous_number_of_nodes + index].add_after_x_jobs) == 6) {
        nodes[previous_number_of_nodes + index].id += previous_number_of_nodes;
        if (nodes[previous_number_of_nodes + index].storage_size > *max_node_size)
        {
            *max_node_size = nodes[previous_number_of_nodes + index].storage_size;
        }
        *total_storage_size += nodes[previous_number_of_nodes + index].storage_size;
        initial_node_sizes[previous_number_of_nodes + index] = nodes[previous_number_of_nodes + index].storage_size;
        index++;
    }
    // Update the annual failure rate to become the probability of failure of the node
    for (int i = 0; i < number_of_nodes; i++) {
        nodes[previous_number_of_nodes + i].probability_failure = probability_of_failure(nodes[previous_number_of_nodes + i].probability_failure, data_duration_on_system);
    }

    fclose(file);
}

// Function to read data from file and populate the sizes array
void read_data(const char *filename, double *sizes, int number_of_repetition) {
    #ifdef PRINT
    printf("Iteration 1\n");
    #endif
    
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }

    // Read the header line
    char header[256];
    if (fgets(header, sizeof(header), file) == NULL) {
        perror("Error reading header");
        fclose(file);
        exit(EXIT_FAILURE);
    }

    // Read the file line by line and populate sizes array
    float temp_size;
    int temp_access_type;
    char line[256];
    int size_count = 0;

    while (fgets(line, sizeof(line), file)) {
        // Parse the line
        if (sscanf(line, "%*d,%f,%*f,%*f,%d", &temp_size, &temp_access_type) == 2) {
            if (temp_access_type == 2) {
                sizes[size_count] = temp_size;
                size_count++;
            }
        } else {
            fprintf(stderr, "Error parsing line: %s\n", line);
        }
    }

    fclose(file);
    
    // Process data X times
    for (int i = 1; i < number_of_repetition; i++) {
        #ifdef PRINT
        printf("Iteration %d\n", i + 1);
        #endif
        for (int j = 0; j < size_count; j++) {
            sizes[i*size_count + j] = sizes[j];
        }
    }
}

// Computes an exponential function based on the input values and reference points.
double exponential_function(double x, double x1, double y1, double x2, double y2) {
    // Ensure x1 is not equal to x2
    if (x1 == x2) {
        fprintf(stderr, "Error: x1 cannot be equal to x2 in exponential_function\n");
        exit(EXIT_FAILURE);
    }

    // Calculate the exponent
    double exponent = (x - x1) / (x2 - x1);

    // Calculate the y value
    double y = y1 * pow(y2 / y1, exponent);

    return y;
}

// Calculate saturation
double get_system_saturation(int number_of_nodes, double min_data_size, double total_storage_size, double total_remaining_size) {
    double saturation = 1.0 - exponential_function(total_remaining_size, total_storage_size, 1.0, min_data_size, 1.0 / number_of_nodes);
    //~ printf("%f %f %f %f\n", min_data_size, total_storage_size, total_remaining_size, exponential_function(total_remaining_size, total_storage_size, 1.0, min_data_size, 1.0 / number_of_nodes));
    //~ exit(1);
    return saturation;
}

// Helper function to compute factorial
int factorial(int n) {
    int result = 1;
    for (int i = 1; i <= n; i++) {
        result *= i;
    }
    return result;
}

// Function to calculate number of combinations (n choose r)
int combination(int n, int r) {
    if (r > n) return 0;
    return factorial(n) / (factorial(r) * factorial(n - r));
}

// Function to print a combination
void print_combination(Combination *comb) {
    for (int i = 0; i < comb->num_elements; i++) {
        printf("Node ID: %d, Size: %f, Write BW: %d, Read BW: %d, Failure Rate: %f\n",
               comb->nodes[i]->id, comb->nodes[i]->storage_size, comb->nodes[i]->write_bandwidth,
               comb->nodes[i]->read_bandwidth, comb->nodes[i]->probability_failure);
    }
}

// Function to free allocated memory for combinations
void free_combinations(Combination **combinations, int count) {
    for (int i = 0; i < count; i++) {
        free(combinations[i]->nodes);
        free(combinations[i]);
    }
    free(combinations);
}

void create_combinations(Node *nodes, int n, int r, Combination **combinations, int *combination_count) {
    int *indices = malloc(r * sizeof(int));
    if (!indices) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    for (int i = 0; i < r; i++) {
        indices[i] = i;
    }

    while (1) {
        combinations[*combination_count] = malloc(sizeof(Combination));
        combinations[*combination_count]->num_elements = r;
        combinations[*combination_count]->nodes = malloc(r * sizeof(Node*));
        combinations[*combination_count]->probability_failure = malloc(r * sizeof(double));
        combinations[*combination_count]->sum_reliability = 0;
        combinations[*combination_count]->variance_reliability = 0;
        combinations[*combination_count]->write_bandwidth = malloc(r * sizeof(int));
        combinations[*combination_count]->min_remaining_size = DBL_MAX;
        combinations[*combination_count]->min_write_bandwidth = INT_MAX;

        for (int i = 0; i < r; i++) {
            combinations[*combination_count]->nodes[i] = &nodes[indices[i]];
            combinations[*combination_count]->probability_failure[i] = nodes[indices[i]].probability_failure;
            combinations[*combination_count]->sum_reliability += nodes[indices[i]].probability_failure;
            combinations[*combination_count]->variance_reliability += nodes[indices[i]].probability_failure * (1 - nodes[indices[i]].probability_failure);
            combinations[*combination_count]->write_bandwidth[i] = nodes[indices[i]].write_bandwidth;
            if (nodes[indices[i]].storage_size < combinations[*combination_count]->min_remaining_size) {
                combinations[*combination_count]->min_remaining_size = nodes[indices[i]].storage_size;
            }
            if (nodes[indices[i]].write_bandwidth < combinations[*combination_count]->min_write_bandwidth) {
                combinations[*combination_count]->min_write_bandwidth = nodes[indices[i]].write_bandwidth;
            }
        }
        (*combination_count)++;
        
        int i = r - 1;
        
        while (i >= 0 && indices[i] == n - r + i) {
            i--;
        }

        if (i < 0) {
            break;
        }

        indices[i]++;

        for (int j = i + 1; j < r; j++) {
            indices[j] = indices[j - 1] + 1;
        }
    }

    free(indices);
}

// Function to calculate Poisson-Binomial CDF approximation
// This is a simplified version. For accurate calculation, consider using libraries or more complex methods.
double poibin_cdf(int N, int K, double sum_reliability, double variance_reliability) {
    double cdf = 0.0;
    int n = N - K;
    double mean = sum_reliability / N;
    double stddev = sqrt(variance_reliability);
    double z = (n - mean) / stddev;
    cdf = 0.5 * (1 + erf(z / sqrt(2.0))); // Using error function approximation

    return cdf;
}

// Function to check if the reliability threshold is met
bool reliability_thresold_met(int N, int K, double reliability_threshold, double sum_reliability, double variance_reliability) {
    double cdf = poibin_cdf(N, K, sum_reliability, variance_reliability);
    return cdf >= reliability_threshold;
}

int get_max_K_from_reliability_threshold_and_nodes_chosen(int number_of_nodes, float reliability_threshold, double sum_reliability, double variance_reliability) {
    int K;
    for (int i = number_of_nodes - 1; i >= 2; i--) {
        K = i;
        if (reliability_thresold_met(number_of_nodes, K, reliability_threshold, sum_reliability, variance_reliability)) {
            return K;
        }
    }
    return -1;
}

// Function to check if a combination is dominated
bool is_dominated(Combination* a, Combination* b) {
    return (a->size_score >= b->size_score && 
            a->replication_and_write_time >= b->replication_and_write_time && 
            a->storage_overhead >= b->storage_overhead) && 
           (a->size_score > b->size_score || 
            a->replication_and_write_time > b->replication_and_write_time || 
            a->storage_overhead > b->storage_overhead);
}

// Function to find the Pareto front
void find_pareto_front(Combination **combinations, int num_combinations, int *pareto_indices, double pareto_front[][3], int *pareto_count) {
    *pareto_count = 0;
    for (int i = 0; i < num_combinations; i++) {
        
        if (combinations[i]->K == -1) {
            continue;
        }
                
        bool dominated = false;
        for (int j = 0; j < num_combinations; j++) {
            if (combinations[j]->K == -1) {
                continue;
            }
            if (i != j && is_dominated(combinations[i], combinations[j])) {
                dominated = true;
                break;
            }
        }
        if (!dominated) {
            pareto_indices[*pareto_count] = i;
            pareto_front[*pareto_count][0] = combinations[i]->replication_and_write_time;
            pareto_front[*pareto_count][1] = combinations[i]->storage_overhead;
            pareto_front[*pareto_count][2] = combinations[i]->size_score;
            (*pareto_count)++;
        }
    }    
}

void find_min_max_pareto(Combination** combinations, int* pareto_indices, int pareto_count, double* min_size_score, double* max_size_score, double* min_replication_and_write_time, double* max_replication_and_write_time, double* min_storage_overhead, double* max_storage_overhead, int* max_time_index, int* max_space_index, int* max_saturation_index) {
    *min_size_score = DBL_MAX;
    *max_size_score = -DBL_MAX;
    *min_replication_and_write_time = DBL_MAX;
    *max_replication_and_write_time = -DBL_MAX;
    *min_storage_overhead = DBL_MAX;
    *max_storage_overhead = -DBL_MAX;

    for (int i = 0; i < pareto_count; i++) {
        int idx = pareto_indices[i];
        double size_score = combinations[idx]->size_score;
        double replication_and_write_time = combinations[idx]->replication_and_write_time;
        double storage_overhead = combinations[idx]->storage_overhead;

        if (size_score < *min_size_score) {
            *min_size_score = size_score;
        }
        if (size_score > *max_size_score) {
            *max_size_score = size_score;
            *max_saturation_index = i;
        }
        if (replication_and_write_time < *min_replication_and_write_time) {
            *min_replication_and_write_time = replication_and_write_time;
        }
        if (replication_and_write_time > *max_replication_and_write_time) {
            *max_replication_and_write_time = replication_and_write_time;
            *max_time_index = i;
        }
        if (storage_overhead < *min_storage_overhead) {
            *min_storage_overhead = storage_overhead;
        }
        if (storage_overhead > *max_storage_overhead) {
            *max_storage_overhead = storage_overhead;
            *max_space_index = i;
        }
    }
}

void algorithm4(int number_of_nodes, Node* nodes, float reliability_threshold, double size, double max_node_size, double min_data_size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, Combination **combinations, int total_combinations, double* total_remaining_size, double total_storage_size, int closest_index, RealRecords* records_array, LinearModel* models, int nearest_size, DataList* list, int data_id) {
    int i = 0;
    int j = 0;
    double chunk_size = 0;
    double one_on_number_of_nodes = 1.0/number_of_nodes;
    bool valid_solution = false;
    
    // Heart of the function
    struct timeval start, end;
    gettimeofday(&start, NULL);
    long seconds, useconds;
    
    *N = -1;
    *K = -1;
    
    // 1. Get system saturation
    //~ double system_saturation = get_system_saturation(number_of_nodes, min_data_size, total_storage_size, *total_remaining_size);    
    #ifdef PRINT
    printf("System saturation = %f\n", system_saturation);
    printf("Data size = %f\n", size);
    #endif
    
    // 2. Iterates over a range of nodes combination
    for (i = 0; i < total_combinations; i++) {
        *K = get_max_K_from_reliability_threshold_and_nodes_chosen(combinations[i]->num_elements, reliability_threshold, combinations[i]->sum_reliability, combinations[i]->variance_reliability);
        #ifdef PRINT
        printf("Max K for combination %d is %d\n", i, *K);
        #endif
        
        // Reset from last expe the values used in pareto front
        combinations[i]->storage_overhead = 0.0;
        combinations[i]->size_score = 0.0;
        combinations[i]->replication_and_write_time = 0.0;
        combinations[i]->transfer_time_parralelized = 0.0;
        combinations[i]->chunking_time = 0.0;
        combinations[i]->K = *K;
        
        if (*K != -1) {
            chunk_size = size/(*K);
            #ifdef PRINT
            printf("Chunk size: %f\n", chunk_size);
            #endif
            if (combinations[i]->min_remaining_size - chunk_size >= 0) {
                valid_solution = true;
                for (j = 0; j < combinations[i]->num_elements; j++) {
                    combinations[i]->size_score += 1.0 - exponential_function(combinations[i]->nodes[j]->storage_size - chunk_size, max_node_size, 1, min_data_size, one_on_number_of_nodes);
                    //~ printf("sat of node %d %f compared to system: %f\n", j, 1.0 - exponential_function(combinations[i]->nodes[j]->storage_size - chunk_size, max_node_size, 1, min_data_size, one_on_number_of_nodes), system_saturation);
                    #ifdef PRINT
                    printf("%f %f %f %f %f\n", combinations[i]->nodes[j]->storage_size, chunk_size, max_node_size, min_data_size, one_on_number_of_nodes);
                    printf("size_score: %f\n", combinations[i]->size_score);
                    #endif
                }
                combinations[i]->size_score = combinations[i]->size_score/combinations[i]->num_elements;
                //~ printf("Total sat: %f\n", combinations[i]->size_score);
                combinations[i]->chunking_time = predict(models[closest_index], combinations[i]->num_elements, *K, nearest_size, size);
                combinations[i]->transfer_time_parralelized = calculate_transfer_time(chunk_size, combinations[i]->min_write_bandwidth);
                combinations[i]->replication_and_write_time = combinations[i]->chunking_time + combinations[i]->transfer_time_parralelized;
                combinations[i]->storage_overhead = chunk_size*combinations[i]->num_elements;
                #ifdef PRINT
                printf("storage_overhead: %f\n", combinations[i]->storage_overhead);
                printf("replication_and_write_time: %f\n", combinations[i]->replication_and_write_time);
                printf("size_score: %f\n", combinations[i]->size_score);
                #endif
            }
            else {
                combinations[i]->K = -1;
                *K = -1;
            }
        }
    }

    if (valid_solution == true) {
        // 3. Only keep combination on pareto front
        int pareto_indices[total_combinations];
        double pareto_front[total_combinations][3];
        int pareto_count;
        
        find_pareto_front(combinations, total_combinations, pareto_indices, pareto_front, &pareto_count);
        
        #ifdef PRINT
        printf("%d combinations on 3D pareto front. Pareto front indices:\n", pareto_count);
        for (i = 0; i < pareto_count; i++) {
            printf("%d(N%d,K%d): sto:%f sat:%f time:%f (%f and %f chunk size is %f)\n", pareto_indices[i], combinations[pareto_indices[i]]->num_elements, combinations[pareto_indices[i]]->K, combinations[pareto_indices[i]]->storage_overhead, combinations[pareto_indices[i]]->size_score, combinations[pareto_indices[i]]->replication_and_write_time, combinations[pareto_indices[i]]->transfer_time_parralelized, combinations[pareto_indices[i]]->chunking_time, size/combinations[pareto_indices[i]]->K);
        }
        #endif
        
        // Get min and max of each of our 3 parameters
        double min_storage_overhead;
        double max_storage_overhead;
        double min_size_score;
        double max_size_score;
        double min_replication_and_write_time;
        double max_replication_and_write_time;
        int max_time_index;
        int max_space_index;
        int max_saturation_index;
        find_min_max_pareto(combinations, pareto_indices, pareto_count, &min_size_score, &max_size_score, &min_replication_and_write_time, &max_replication_and_write_time, &min_storage_overhead, &max_storage_overhead, &max_time_index, &max_space_index, &max_saturation_index);
        #ifdef PRINT
        printf("Min and max from pareto front are: %f %f %f %f %f %f / max time index:%d max space index:%d\n", min_storage_overhead, max_storage_overhead, min_size_score, max_size_score, min_replication_and_write_time, max_replication_and_write_time, max_time_index, max_space_index);
        #endif
        
        // Compute score with % progress
        //~ double total_progress_storage_overhead = max_storage_overhead - min_storage_overhead;
        //~ double total_progress_size_score = max_size_score - min_size_score;
        //~ double total_progress_replication_and_write_time = max_replication_and_write_time - min_replication_and_write_time;
        //~ #ifdef PRINT
        //~ printf("Progresses are %f %f %f\n", total_progress_storage_overhead, total_progress_size_score, total_progress_replication_and_write_time);
        //~ #endif
        //~ double time_score = 0;
        //~ double space_score = 0;
        //~ double total_score = 0;
        //~ double max_score = -DBL_MAX;
        //~ int idx = 0;
        
        int best_index = -1;
        
        // Getting combination with best score using pareto front progress
        //~ for (i = 0; i < pareto_count; i++) {
            //~ idx = pareto_indices[i];
            //~ if (total_progress_replication_and_write_time > 0) {  // In some cases, when there are not enough solution or if they are similar the total progress is 0. As we don't want to divide by 0, we keep the score at 0 for the corresponding value as no progress could be made
                //~ time_score = 100 - ((combinations[idx]->replication_and_write_time - min_replication_and_write_time)*100)/total_progress_replication_and_write_time;
            //~ }
            
            //~ if (total_progress_storage_overhead > 0) {
                //~ space_score = 100 - ((combinations[idx]->storage_overhead - min_storage_overhead)*100)/total_progress_storage_overhead;
            //~ }
            //~ if (total_progress_size_score > 0) {
                //~ space_score += 100 - ((combinations[idx]->size_score - min_size_score)*100)/total_progress_size_score;
            //~ }

            //~ // first idea
            //~ // total_score = time_score + (space_score/2.0)*system_saturation;
            
            //~ // alternative idea
            //~ total_score = (1 - system_saturation)*time_score + space_score/2.0;
            
            //~ if (max_score < total_score) { // Higher score the better
                //~ max_score = total_score;
                //~ best_index = idx;
            //~ }
        //~ }
        
        // Getting combination with best score using 3D pareto knee bend angle max todo use threshold?
        // TODO if we keep this ne need to compute system saturation
        double knee_point[3];
        //~ printf("max_time_index %d, max_saturation_index %d\n", max_time_index, max_saturation_index);
        best_index = pareto_indices[find_knee_point_3d(pareto_front, pareto_count, knee_point, max_time_index, max_saturation_index)];
        //~ printf("Knee Point: %d (%.2f, %.2f, %.2f)\n", best_index, knee_point[0], knee_point[1], knee_point[2]);

        #ifdef PRINT
        printf("Best index is %d with N%d K%d\n", best_index, combinations[best_index]->num_elements, combinations[best_index]->K);
        printf("..\n");
        #endif

        *N = combinations[best_index]->num_elements;
        *K = combinations[best_index]->K;
        gettimeofday(&end, NULL);
        
        double total_upload_time_to_print = 0;
        
        // Writing down the results
        if (*N != -1 && *K != -1) {
            chunk_size = size/(*K);
            *number_of_data_stored += 1;
            *total_N += *N;
            *total_storage_used += chunk_size*(*N);
            *total_remaining_size -= chunk_size*(*N);
            *total_parralelized_upload_time += chunk_size/combinations[best_index]->min_write_bandwidth;
            for (i = 0; i < combinations[best_index]->num_elements; i++) {
                total_upload_time_to_print += chunk_size/combinations[best_index]->nodes[i]->write_bandwidth;
                combinations[best_index]->nodes[i]->storage_size -= chunk_size;                
            }
            add_node_to_print(list, data_id, size, total_upload_time_to_print, combinations[best_index]->transfer_time_parralelized, combinations[best_index]->chunking_time, *N, *K);
            //~ printf("Added data to print %d\n", head_data_to_print->id);
            *total_upload_time += total_upload_time_to_print;
            //~ printf("Added %f to upload time\n", total_upload_time_to_print);
            combinations[best_index]->min_remaining_size -= chunk_size;
        }
    }
    else {
        gettimeofday(&end, NULL);
    }
    seconds  = end.tv_sec  - start.tv_sec;
    useconds = end.tv_usec - start.tv_usec;
    *total_scheduling_time += seconds + useconds/1000000.0;
}

void algorithm2(int number_of_nodes, Node* nodes, float reliability_threshold, double size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, Combination **combinations, int total_combinations, double total_storage_size, int closest_index, RealRecords* records_array, LinearModel* models, int nearest_size, DataList* list, int data_id) {
    int i = 0;
    int j = 0;
    double chunk_size = 0;
    bool valid_solution = false;
    
    // Heart of the function
    struct timeval start, end;
    gettimeofday(&start, NULL);
    long seconds, useconds;
    int best_index = -1;
    double min_time = INT_MAX;
    
    *N = -1;
    *K = -1;
        
    // 1. Iterates over a range of nodes combination
    for (i = 0; i < total_combinations; i++) {
        *K = get_max_K_from_reliability_threshold_and_nodes_chosen(combinations[i]->num_elements, reliability_threshold, combinations[i]->sum_reliability, combinations[i]->variance_reliability);
        #ifdef PRINT
        printf("Max K for combination %d is %d\n", i, *K);
        #endif
        
        // Reset from last expe the values used in pareto front
        combinations[i]->total_transfer_time = 0.0;
        combinations[i]->chunking_time = 0.0;
        combinations[i]->K = *K;
        
        if (*K != -1) {
            chunk_size = size/(*K);
            if (combinations[i]->min_remaining_size - chunk_size >= 0) {
                valid_solution = true;
                for (j = 0; j < combinations[i]->num_elements; j++) {
                    combinations[i]->total_transfer_time += calculate_transfer_time(chunk_size, combinations[i]->nodes[j]->write_bandwidth);
                }
                combinations[i]->chunking_time = predict(models[closest_index], combinations[i]->num_elements, *K, nearest_size, size);
                if (min_time > combinations[i]->chunking_time + combinations[i]->total_transfer_time) {
                    min_time = combinations[i]->chunking_time + combinations[i]->total_transfer_time;
                    best_index = i;
                }
            }
            else {
                combinations[i]->K = -1;
                *K = -1;
            }
        }
    }
    
    if (valid_solution == true) {
        *N = combinations[best_index]->num_elements;
        *K = combinations[best_index]->K;
        gettimeofday(&end, NULL);
        
        double total_upload_time_to_print = 0;
        
        // Writing down the results
        if (*N != -1 && *K != -1) {
            chunk_size = size/(*K);
            *number_of_data_stored += 1;
            *total_N += *N;
            *total_storage_used += chunk_size*(*N);
            *total_parralelized_upload_time += chunk_size/combinations[best_index]->min_write_bandwidth;
            for (i = 0; i < combinations[best_index]->num_elements; i++) {
                total_upload_time_to_print += chunk_size/combinations[best_index]->nodes[i]->write_bandwidth;
                combinations[best_index]->nodes[i]->storage_size -= chunk_size;                
            }
            add_node_to_print(list, data_id, size, total_upload_time_to_print, combinations[best_index]->transfer_time_parralelized, combinations[best_index]->chunking_time, *N, *K);
            *total_upload_time += total_upload_time_to_print;
            combinations[best_index]->min_remaining_size -= chunk_size;
        }
    }
    else {
        gettimeofday(&end, NULL);
    }
    seconds  = end.tv_sec  - start.tv_sec;
    useconds = end.tv_usec - start.tv_usec;
    *total_scheduling_time += seconds + useconds/1000000.0;
}

// Function to free the memory allocated for RealRecords
void free_records(RealRecords *records) {
    free(records->n);
    free(records->k);
    free(records->avg_time);
}

int extract_integer_from_filename(const char *filename) {
    // Create a copy of the filename to modify
    char *filename_copy = strdup(filename);
    if (filename_copy == NULL) {
        perror("Memory allocation failed");
        exit(EXIT_FAILURE);
    }

    // Find the position of the last '/' character
    char *base_name = strrchr(filename_copy, '/');
    if (base_name != NULL) {
        // Move past the '/' character
        base_name++;
    } else {
        base_name = filename_copy; // No '/' found, use the entire string
    }

    // Remove the ".csv" extension
    char *extension = strstr(base_name, ".csv");
    if (extension != NULL) {
        *extension = '\0'; // Terminate the string before ".csv"
    }

    // Convert the remaining part of the string to an integer
    int result = atoi(base_name);

    // Clean up
    free(filename_copy);

    return result;
}

// Function to read records from file and populate the RealRecords structure
void read_records(const char *filename, RealRecords *records) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        perror("Error opening file");
        exit(EXIT_FAILURE);
    }

    // Initialize the size
    records->size = extract_integer_from_filename(filename);
    
    // Allocate memory for arrays
    int num_rows = 171; // number of rows in the file
    records->n = (double *)malloc(num_rows * sizeof(double));
    records->k = (double *)malloc(num_rows * sizeof(double));
    records->avg_time = (double *)malloc(num_rows * sizeof(double));

    if (records->n == NULL || records->k == NULL || records->avg_time == NULL) {
        perror("Memory allocation failed");
        fclose(file);
        exit(EXIT_FAILURE);
    }

    // Read and ignore the header line
    char header[256];
    if (fgets(header, sizeof(header), file) == NULL) {
        perror("Error reading header");
        fclose(file);
        exit(EXIT_FAILURE);
    }

    // Read the file line by line and populate the arrays
    int i = 0;
    while (i < num_rows && fscanf(file, "%lf %lf %lf", &records->n[i], &records->k[i], &records->avg_time[i]) == 3) {
        i++;
    }
    
    if (i != num_rows) {
        fprintf(stderr, "Error: Number of rows read %d does not match expected number of rows.\n", i);
        fclose(file);
        exit(EXIT_FAILURE);
    }

    fclose(file);
}

void find_closest(int target, int* nearest_size, int* closest_index) {
    // The array of numbers to compare against
    int numbers[] = {1, 10, 50, 100, 200, 400};
    int size = sizeof(numbers) / sizeof(numbers[0]);

    // Initialize the closest number to the first element
    int min_diff = abs(target - numbers[0]);

    // Iterate over the array to find the closest number
    for (int i = 1; i < size; i++) {
        int diff = abs(target - numbers[i]);
        if (diff < min_diff) {
            min_diff = diff;
            *nearest_size = numbers[i];
            *closest_index = i;
        }
    }
}

int main(int argc, char *argv[]) {
    int i = 0;
    if (argc < 8) {
        fprintf(stderr, "Usage: %s <input_node> <input_data> <data_duration_on_system> <reliability_threshold> <number_of_repetition> <algorithm> <input_supplementary_node>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *input_node = argv[1];
    const char *input_data = argv[2];
    double data_duration_on_system = atof(argv[3]);
    double reliability_threshold = atof(argv[4]);
    int number_of_repetition = atoi(argv[5]);
    int algorithm = atoi(argv[6]); // 4 is alg4 (drex) and 2 is alg 2 (time)
    const char *input_supplementary_node = argv[7];
    printf("Data have to stay %f days on the system. Reliability threshold is %f. Number of repetition is %d\n", data_duration_on_system, reliability_threshold, number_of_repetition);
    
    DataList list;
    init_list(&list);
    
    // Step 1: Count the number of lines
    int count = count_lines_with_access_type(input_data);
    count = count*number_of_repetition;
    int number_of_initial_nodes = count_nodes(input_node);
    int number_of_supplementary_nodes = count_nodes(input_supplementary_node);
    int number_of_nodes = number_of_initial_nodes + number_of_supplementary_nodes;

    printf("number_of_initial_nodes: %d\n", number_of_initial_nodes);
    printf("number_of_supplementary_nodes: %d\n", number_of_supplementary_nodes);
    printf("number_of_nodes: %d\n", number_of_nodes);
    
    // Step 2: Allocate memory
    double *sizes = (double*)malloc(count * sizeof(double));
    if (sizes == NULL) {
        perror("Error allocating memory");
        return EXIT_FAILURE;
    }
    Node *nodes = (Node *)malloc(number_of_nodes * sizeof(Node));
    if (nodes == NULL) {
        perror("Error allocating memory");
        return EXIT_FAILURE;
    }

    // Step 3: Read data into the arrays
    read_data(input_data, sizes, number_of_repetition);
    double total_storage_size = 0;
    double max_node_size = 0;
    double *initial_node_sizes = (double*)malloc(number_of_nodes * sizeof(double));
    read_node(input_node, number_of_initial_nodes, nodes, data_duration_on_system, &max_node_size, &total_storage_size, initial_node_sizes);
    if (number_of_supplementary_nodes > 0) {
        read_supplementary_node(input_supplementary_node, number_of_supplementary_nodes, nodes, data_duration_on_system, &max_node_size, &total_storage_size, initial_node_sizes, number_of_initial_nodes);
    }
    
    // Print the collected data
    #ifdef PRINT
    printf("There are %d data in W mode:\n", count);
    for (i = 0; i < count; i++) {
        printf("%.2f\n", sizes[i]);
    }
    #endif
    
    //~ #ifdef PRINT
    for (i = 0; i < number_of_nodes; i++) {
        printf("Node %d: storage_size=%f, write_bandwidth=%d, read_bandwidth=%d, probability_failure=%f\n",
               nodes[i].id, nodes[i].storage_size, nodes[i].write_bandwidth,
               nodes[i].read_bandwidth, nodes[i].probability_failure);
        //~ printf("initial_node_sizes %d: %f\n", i, initial_node_sizes[i]);
    }
    printf("Max node size is %f\n", max_node_size);
    printf("Total storage size is %f\n", total_storage_size);
    //~ #endif
    
    // Variables used in algorithm4
    double min_data_size = DBL_MAX;
    int N;
    int K;
    int j = 0;
    const char *output_filename = "output_drex_only.csv";
    
    const char *alg_to_print = "";
    if (algorithm == 4) {
        alg_to_print = "alg4";
    }
    else {
        alg_to_print = "alg2";
    }
    double total_scheduling_time = 0;
    double total_storage_used = 0;
    double total_upload_time = 0;
    double total_parralelized_upload_time = 0;
    int number_of_data_stored = 0;
    int total_N = 0; // Number of chunks
    
    // Calculate total number of combinations
    int total_combinations = 0;
    int min_number_node_in_combination = 2;
    int max_number_node_in_combination = number_of_initial_nodes;
    for (i = min_number_node_in_combination; i <= max_number_node_in_combination; i++) {
        total_combinations += combination(number_of_initial_nodes, i);
    }

    #ifdef PRINT
    printf("There are %d possible combinations\n", total_combinations);
    #endif
    
    // Generate all possibles combinations
    Combination **combinations = NULL;
    // Allocate memory for storing all combinations
    combinations = malloc(total_combinations * sizeof(Combination *));
    if (combinations == NULL) {
        perror("Error allocating memory for combinations");
        exit(EXIT_FAILURE);
    }
    int combination_count = 0;
    for (i = min_number_node_in_combination; i <= max_number_node_in_combination; i++) {
        create_combinations(nodes, number_of_initial_nodes, i, combinations, &combination_count);
    }
    //~ printf("max_number_node_in_combination = %d\n", max_number_node_in_combination);
    
    #ifdef PRINT
    for (i = 0; i < total_combinations; i++) {
        printf("Combination %d: ", i + 1);
        for (j = 0; j < combinations[i]->num_elements; j++) {
            printf("%d ", combinations[i]->nodes[j]->id);
            printf("%d - ", combinations[i]->write_bandwidth[j]);
        }
        printf("\n");
    }
    #endif
    //~ exit(1);
    // Prediction of chunking time
    // My code
    // Filling a struct with our prediction records
    // Define the number of files
    int num_files = 6;
    const char *filenames[] = {
        "data/1MB.csv", 
        "data/10MB.csv", 
        "data/50MB.csv",
        "data/100MB.csv",
        "data/200MB.csv",
        "data/400MB.csv"
    };
    // Array to hold RealRecords for each file
    RealRecords *records_array = (RealRecords *)malloc(num_files * sizeof(RealRecords));
    if (records_array == NULL) {
        perror("Memory allocation failed for records array");
        exit(EXIT_FAILURE);
    }
    // Read records from each file
    for (i = 0; i < num_files; i++) {
        read_records(filenames[i], &records_array[i]);
    }
    // Print the data to verify (example for the first file)
    #ifdef PRINT
    for (i = 0; i < 171; i++) {
        printf("File %s, Row %d: n: %.2f, k: %.2f, avg_time: %.6f\n", filenames[0], i, records_array[0].n[i], records_array[0].k[i], records_array[0].avg_time[i]);
    }
    #endif
    
    LinearModel *models = (LinearModel *)malloc(num_files * sizeof(LinearModel));
    double c0, c1, c2;
    for (i = 0; i < num_files; i++) {
        c0 = 0;
        c1 = 0;
        c2 = 0;
        if (fit_linear_model(&records_array[i], &c0, &c1, &c2) == 0) {
             #ifdef PRINT
            printf("Fitted coefficients for i=%d: c0 = %f, c1 = %f, c2 = %f\n", i, c0, c1, c2);
            #endif
        } else {
            fprintf(stderr, "Failed to fit linear model.\n");
        }
        models[i].intercept = c0;
        models[i].slope_n = c1;
        models[i].slope_k = c2;
    }

    double total_remaining_size = total_storage_size; // Used for system saturation
    int closest_index = 0;
    int nearest_size = 0;
    
    // Current number of nodes being used. Will be updated when next node time is reached
    int current_number_of_nodes = number_of_initial_nodes;
    
    /** Simulation main loop **/
    for (i = 0; i < count; i++) {
        //~ printf("current_number_of_nodes = %d\n", current_number_of_nodes);
        if (min_data_size > sizes[i]) {
            min_data_size = sizes[i];
        }
        
        // If we reached a threshold for a new node, we add it to the list of combinations
        if (number_of_supplementary_nodes > 0 && i == nodes[current_number_of_nodes].add_after_x_jobs) {
            printf("Adding node %d\n", nodes[current_number_of_nodes].id);
            current_number_of_nodes += 1;
            // Calculate total number of combinations
            total_combinations = 0;
            max_number_node_in_combination = current_number_of_nodes;
            for (j = min_number_node_in_combination; j <= max_number_node_in_combination; j++) {
                total_combinations += combination(current_number_of_nodes, j);
            }
            #ifdef PRINT
            printf("There are %d possible combinations\n", total_combinations);
            #endif
            // Generate all possibles combinations
            free(combinations);
            // Allocate memory for storing all combinations
            combinations = malloc(total_combinations * sizeof(Combination *));
            if (combinations == NULL) {
                perror("Error allocating memory for combinations");
                exit(EXIT_FAILURE);
            }
            combination_count = 0;
            for (j = min_number_node_in_combination; j <= max_number_node_in_combination; j++) {
                create_combinations(nodes, current_number_of_nodes, j, combinations, &combination_count);
            }
        }
        
        find_closest(sizes[i], &nearest_size, &closest_index);
        
        if (algorithm == 2) {
            algorithm2(current_number_of_nodes, nodes, reliability_threshold, sizes[i], &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, combinations, total_combinations, total_storage_size, closest_index, records_array, models, nearest_size, &list, i);
        }
        else if (algorithm == 4) {
            algorithm4(current_number_of_nodes, nodes, reliability_threshold, sizes[i], max_node_size, min_data_size, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, combinations, total_combinations, &total_remaining_size, total_storage_size, closest_index, records_array, models, nearest_size, &list, i);
        }
        else {
            printf("Algorithm %d not valid\n", algorithm);
        }
        #ifdef PRINT
        printf("Algorithm %d chose N = %d and K = %d\n", algorithm, N, K);
        #endif
        //~ if (i%10000 == 0) {
        if (i%100 == 0) {
            printf("%d/%d\n", i, count);
        }
    }
    #ifdef PRINT
    printf("Total scheduling time was %f\n", total_scheduling_time);
    #endif

    // Writting the data per data outputs
    double total_chunking_time = 0;
    
    if (algorithm == 4) {
        write_linked_list_to_file(&list, "output_alg4_stats.csv", &total_chunking_time);
    }
    else {
        write_linked_list_to_file(&list, "output_alg2_stats.csv", &total_chunking_time);
    }
    
    // Writting the general outputs
    FILE *file = fopen(output_filename, "a");
    if (file == NULL) {
        perror("Error opening file");
        return EXIT_FAILURE;
    }

    fprintf(file, "%s, %f, %f, %f, %f, %d, %d, %f, %f, %f, \"[", alg_to_print, total_scheduling_time, total_storage_used, total_upload_time, total_parralelized_upload_time, number_of_data_stored, total_N, total_storage_used / number_of_data_stored, total_upload_time / number_of_data_stored, (double)total_N / number_of_data_stored);
    for (i = 0; i < number_of_nodes - 1; i++) {
        fprintf(file, "%f, ", initial_node_sizes[i]);
    }
    fprintf(file, "%f]\", \"[", initial_node_sizes[i]);
    for (i = 0; i < number_of_nodes - 1; i++) {
        fprintf(file, "%f, ", nodes[i].storage_size);
    }
    fprintf(file, "%f]\"", nodes[i].storage_size);
    fprintf(file, ", %f, %f, %f\n", total_chunking_time, total_chunking_time / number_of_data_stored, total_parralelized_upload_time / number_of_data_stored);
    fclose(file);
    
    // Free allocated memory
    free(sizes);
    free(nodes);
    for (int i = 0; i < num_files; i++) {
        free(records_array[i].n);
        free(records_array[i].k);
        free(records_array[i].avg_time);
    }
    free(records_array);
    free(models);
    
    printf("Success\n");
    return EXIT_SUCCESS;
}
