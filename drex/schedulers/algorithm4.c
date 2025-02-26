#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <limits.h>
#include <math.h>
#include <stdbool.h>
#include <string.h>
#include "../utils/prediction.h"
#include "algorithm4.h"
#include "../utils/pareto_knee.h"
#include "../utils/k_means_clustering.h"
#include "../utils/combinations.h"
#include "../utils/remove_node.h"
#include "bogdan_balance_penalty.h"
#include "algorithm1.h"
#include "least_used_node.h"
#include "random.h"
#include "hdfs.h"
#include "glusterfs.h"
#include "optimal_schedule.h"
#include <sys/time.h>

int global_current_data_value;

double get_total_remaining_size(Node* nodes, int current_number_of_nodes) {
    double new_total_remaining_size = 0;
    for (int i = 0; i < current_number_of_nodes; i++) {
        //~ printf("Adding %f from node %d\n", nodes[i].storage_size, nodes[i].id);
        new_total_remaining_size += nodes[i].storage_size;
    }
    return new_total_remaining_size;
}

// Initialize the chunk list in the node
void init_chunk_list(Node* node) {
    node->chunks = (ChunkList*)malloc(sizeof(ChunkList));
    if (node->chunks == NULL) {
        perror("Failed to allocate memory for chunk list");
        exit(EXIT_FAILURE);
    }
    node->chunks->head = NULL;
}

// Function to add a chunk to a single node's chunk list
void add_chunk_to_node(Node* node, int chunk_id, double size, int num_of_nodes_used, int* nodes_used, double original_data_size) {
    Chunk* new_chunk = (Chunk*)malloc(sizeof(Chunk));
    if (new_chunk == NULL) {
        perror("Failed to allocate memory for new chunk");
        exit(EXIT_FAILURE);
    }

    // Initialize the new chunk
    new_chunk->chunk_id = chunk_id;
    new_chunk->chunk_size = size;
    //~ printf("New chunk %d size is %f\n", chunk_id, new_chunk->chunk_size);
    new_chunk->num_of_nodes_used = num_of_nodes_used;
    new_chunk->nodes_used = malloc(num_of_nodes_used * sizeof(int));
    new_chunk->original_data_size = original_data_size;
    if (new_chunk->nodes_used == NULL) {
        perror("Failed to allocate memory for nodes_used");
        free(new_chunk);
        exit(EXIT_FAILURE);
    }

    // Copy the node IDs into the new chunk
    for (int i = 0; i < num_of_nodes_used; i++) {
        new_chunk->nodes_used[i] = nodes_used[i];
        //~ printf("Added in add_chunk_to_node to node %d\n", new_chunk->nodes_used[i]);
    }

    // Insert the new chunk at the beginning of the chunk list
    new_chunk->next = node->chunks->head;
    node->chunks->head = new_chunk;
}

// Function to add shared chunks to multiple nodes
void add_shared_chunks_to_nodes(int* nodes_used, int num_of_nodes_used, int chunk_id, double chunk_size, Node* nodes, int number_of_nodes, double original_data_size) {
    // Add a separate chunk to each node
    int i = 0;
    int j = 0;
    
    for (i = 0; i < num_of_nodes_used; i++) {
        for (j = 0; j < number_of_nodes; j++) {
            if (nodes[j].id == nodes_used[i]) {
                break;
            }
        }
        add_chunk_to_node(&nodes[j], chunk_id, chunk_size, num_of_nodes_used, nodes_used, original_data_size);
    }
}

// Function to add shared chunks to multiple nodes
void add_shared_chunks_to_nodes_3_replication(int* nodes_used, int num_of_nodes_used, int chunk_id, double* size_to_stores, Node* nodes, int number_of_nodes, double original_data_size) {
    int i = 0;
    int j = 0;
    
    for (i = 0; i < num_of_nodes_used; i++) {
        for (j = 0; j < number_of_nodes; j++) {
            if (nodes[j].id == nodes_used[i]) {
                break;
            }
        }
        add_chunk_to_node(&nodes[j], chunk_id, size_to_stores[i], num_of_nodes_used, nodes_used, original_data_size);
    }
}

void remove_chunk_from_node(int* index_node_used, int index_count, int chunk_id, Node* nodes, int number_of_nodes) {
    // Allocate memory for the new array
    int* copied_indices = (int*)malloc(index_count * sizeof(int));
    if (copied_indices == NULL) {
        printf("Memory allocation failed\n");
        return;
    }

    // Copy the contents of index_node_used into copied_indices
    for (int i = 0; i < index_count; i++) {
        copied_indices[i] = index_node_used[i];
    }

    // Now, you can use copied_indices for further processing
    for (int i = 0; i < index_count; i++) {
        int current_node_index = copied_indices[i];
        int j = 0;

        // Find the node to remove from
        for (j = 0; j < number_of_nodes; j++) {
            if (nodes[j].id == current_node_index) {
                break;
            }
        }

        if (j == number_of_nodes) {
            printf("Node with id %d not found\n", current_node_index);
            continue;
        }

        if (nodes[j].chunks == NULL || nodes[j].chunks->head == NULL) {
            printf("No chunks to remove in node %d\n", current_node_index);
            continue; // No chunks to remove
        }

        Chunk* current = nodes[j].chunks->head;
        Chunk* prev = NULL;

        // Traverse the list to find the chunk with the given chunk_id
        while (current != NULL) {
            if (current->chunk_id == chunk_id) {
                //~ printf("Remove chunk %d from node %d in remove_chunk\n", chunk_id, current_node_index);
                // Found the chunk, remove it from the list
                if (prev == NULL) {
                    // The chunk is the first in the list
                    nodes[j].chunks->head = current->next;
                } else {
                    // The chunk is in the middle or at the end of the list
                    prev->next = current->next;
                }

                // Free the memory allocated for this chunk
                free(current->nodes_used);
                free(current);
                break;  // Exit the loop since the chunk is removed
            }

            // Move to the next chunk
            prev = current;
            current = current->next;
        }
    }

    // Free the memory allocated for copied_indices
    free(copied_indices);
}

DataToPrint* create_node(int id, double size, double total_transfer_time, double transfer_time_parralelized, double chunking_time, int N, int K, double total_read_time, double read_time_parralelized, double reconstruct_time) {
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
    new_node->total_read_time = total_read_time;
    new_node->read_time_parralelized = read_time_parralelized;
    new_node->reconstruct_time = reconstruct_time;
    new_node->next = NULL;
    return new_node;
}

TimeToPrint* create_node_time(int time, double size_stored) {
    TimeToPrint *new_node = (TimeToPrint*)malloc(sizeof(TimeToPrint));
    if (!new_node) {
        perror("Failed to allocate memory for new node");
        exit(EXIT_FAILURE);
    }
    new_node->time = time;
    new_node->size_stored = size_stored;
    new_node->next = NULL;
    return new_node;
}

void init_list(DataList *list) {
    list->head = NULL;
    list->tail = NULL;
}

void init_list_time(TimeList *list) {
    list->head = NULL;
    list->tail = NULL;
}

// Function to print the chunks of all nodes
void print_all_chunks(Node* nodes, int num_nodes) {
    for (int i = 0; i < num_nodes; i++) {
        if (nodes[i].chunks->head != NULL) {
            printf("Node %d: ", nodes[i].id);
            Chunk* current_chunk = nodes[i].chunks->head;
            while (current_chunk != NULL) {
                printf("Chunk %d %f ", current_chunk->chunk_id, current_chunk->chunk_size);
                printf("%d nodes used ( ", current_chunk->num_of_nodes_used);
                for (int j = 0; j < current_chunk->num_of_nodes_used; j++) {
                    printf("%d ", current_chunk->nodes_used[j]);
                }
                printf(") // ");
                current_chunk = current_chunk->next;
            }
            printf("\n");  // Separate nodes by a newline
        }
    }
}

void add_time_to_print(TimeList *list, int time, double size_stored) {
    TimeToPrint *new_node = create_node_time(time, size_stored);
    if (list->tail) {
        list->tail->next = new_node;
    } else {
        list->head = new_node;
    }
    list->tail = new_node;
}

void add_node_to_print(DataList *list, int id, double size, double total_transfer_time, double transfer_time_parralelized, double chunking_time, int N, int K, double total_read_time, double read_time_parralelized, double reconstruct_time) {
    DataToPrint *new_node = create_node(id, size, total_transfer_time, transfer_time_parralelized, chunking_time, N, K, total_read_time, read_time_parralelized, reconstruct_time);
    //~ printf("create node with %f\n", chunking_time);
    if (list->tail) {
        list->tail->next = new_node;
    } else {
        list->head = new_node;
    }
    list->tail = new_node;
}

/**
 * Write in a file the details of the execution
 **/
void write_linked_list_to_file(DataList *list, const char *filename, double* total_chunking_time, double* total_reconstruct_time) {
    FILE *file = fopen(filename, "w");
    if (!file) {
        perror("Failed to open file");
        exit(EXIT_FAILURE);
    }
    
    fprintf(file, "ID,Size,Total_Transfer_Time,Transfer_Time_Parralelized,Chunking_Time,N,K,Total_Read_Time,Read_Time_Parralelized,Reconstruct_Time\n");
    DataToPrint *current = list->head;
    while (current) {
        //~ printf("%f\n", current->chunking_time);
        fprintf(file, "%d,%f,%f,%f,%f,%d,%d,%f,%f,%f\n", current->id, current->size, current->total_transfer_time, current->transfer_time_parralelized, current->chunking_time, current->N, current->K, current->total_read_time, current->read_time_parralelized, current->reconstruct_time);
        if (!isinf(current->chunking_time)) {
            *total_chunking_time += current->chunking_time;
        }
        if (!isinf(current->reconstruct_time)) {
            *total_reconstruct_time += current->reconstruct_time;
        }
        current = current->next;
    }
    fclose(file);
}

/**
 * Write in a file the details of the execution
 **/
void write_linked_list_time_to_file(TimeList *list, const char *filename) {
    FILE *file = fopen(filename, "w");
    if (!file) {
        perror("Failed to open file");
        exit(EXIT_FAILURE);
    }
    
    fprintf(file, "Time, Size_stored\n");
    TimeToPrint *current = list->head;
    while (current) {
        fprintf(file, "%d, %f\n", current->time, current->size_stored);
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
        printf("Error opening file %s", filename);
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

double calculate_daily_failure_rate(double annual_failure_rate) {
    return 1 - pow(1 - annual_failure_rate/100, 1.0 / 365);
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
        printf("Error opening file %s", filename);
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
    // Add a daily failure rate
    for (int i = 0; i < number_of_nodes; i++) {
        //~ printf("NODE %d of AFR %f\n", nodes[i].id, nodes[i].probability_failure);
        //~ nodes[i].daily_failure_rate = nodes[i].probability_failure / 365.0;
        nodes[i].daily_failure_rate = calculate_daily_failure_rate(nodes[i].probability_failure);
        nodes[i].probability_failure = probability_of_failure(nodes[i].probability_failure, data_duration_on_system);
        init_chunk_list(&nodes[i]);
        //~ printf("Prob of failure over 365 days: %f, DFR: %f\n", nodes[i].probability_failure, nodes[i].daily_failure_rate);
    }

    fclose(file);
}

void read_supplementary_node(const char *filename, int number_of_nodes, Node *nodes, double data_duration_on_system, double* initial_node_sizes, int previous_number_of_nodes, int* supplementary_nodes_next_time, double* total_storage_supplementary_nodes, double* max_node_size_supplementary_nodes) {
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        printf("Error opening file %s", filename);
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
        //~ if (nodes[previous_number_of_nodes + index].storage_size > *max_node_size)
        //~ {
            max_node_size_supplementary_nodes[index] = nodes[previous_number_of_nodes + index].storage_size;
        //~ }
        total_storage_supplementary_nodes[index] = nodes[previous_number_of_nodes + index].storage_size;
        initial_node_sizes[previous_number_of_nodes + index] = nodes[previous_number_of_nodes + index].storage_size;
        
        supplementary_nodes_next_time[index] = nodes[previous_number_of_nodes + index].add_after_x_jobs;
        //~ printf("%d at %d\n", nodes[previous_number_of_nodes + index].add_after_x_jobs, index);
        
        index++;
    }
    // Update the annual failure rate to become the probability of failure of the node
    for (int i = 0; i < number_of_nodes; i++) {
        nodes[previous_number_of_nodes + i].probability_failure = probability_of_failure(nodes[previous_number_of_nodes + i].probability_failure, data_duration_on_system);
        init_chunk_list(&nodes[previous_number_of_nodes + i]);
    }

    fclose(file);
}

/** **/
double generate_reliability() {
    //~ int nines_count = rand() % 10; // Randomly choose between 0 and 9 (previously 6) nines
    //~ int nines_count = rand() % 7; // Randomly choose between 0 and 6 nines
    int nines_count = rand() % 6; // Randomly choose between 0 and 6 nines
    double base_reliability = 0;
    // Create the base with the selected number of nines
    for (int i = 0; i < nines_count; i++) {
        base_reliability += 0.9/(pow(10.0, i));
        //~ printf("+= %f\n", 0.9/(pow(10, i)));
    }
    //~ if (nines_count == 7) {
        //~ base_reliability = 0.9999999;
    //~ }
    //~ base_reliability+= 0.001;
    //~ printf("base_reliability = %.9f\n", base_reliability);
    // Generate a random value between base_reliability and 1.0
    double random_reliability = base_reliability + ((double)rand() / RAND_MAX) * (1.0 - base_reliability);
    //~ printf("random_reliability = %.9f\n", random_reliability);
    //~ if (nines_count == 9) { return base_reliability; }
    //~ if (nines_count == 7) { return base_reliability; }
    return random_reliability;
}

// Function to read data from file and populate the sizes array
void read_data(const char *filename, double *sizes, int *submit_times, int number_of_repetition, double* target_reliability) {
    #ifdef PRINT
    printf("Iteration 1\n");
    #endif
    
    FILE *file = fopen(filename, "r");
    if (file == NULL) {
        printf("Error opening file %s", filename);
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
    float temp_submit_time;
    int temp_access_type;
    char line[256];
    int size_count = 0;

    while (fgets(line, sizeof(line), file)) {
        // Parse the line
        if (sscanf(line, "%*d,%f,%f,%*f,%d", &temp_size, &temp_submit_time, &temp_access_type) == 3) {
            if (temp_access_type == 2) {
                sizes[size_count] = temp_size;
                submit_times[size_count] = (int)roundf(temp_submit_time);
                target_reliability[size_count] = generate_reliability();
                //~ printf("target_reliability[size_count] %f\n", target_reliability[size_count]); if (size_count > 30) { exit(1); }
                if (submit_times[size_count] > 1947483647) { printf("ERROR: Time too big use a long or double for submit times\n"); exit(1); }
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
            submit_times[i*size_count + j] = (submit_times[size_count-1]*i) + submit_times[j] + 1;
            target_reliability[i*size_count + j] = generate_reliability();
            
            if (submit_times[i*size_count + j] > 1947483647) { printf("ERROR: Time too big use a long or double for submit times\n"); exit(1); }
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

// Function to calculate factorial
unsigned long long factorial(int n) {
    if (n == 0 || n == 1) return 1;
    unsigned long long result = 1;
    for (int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

// Function to print a combination
void print_combination(Combination *comb) {
    for (int i = 0; i < comb->num_elements; i++) {
        printf("Node ID: %d, Size: %f, Write BW: %d, Read BW: %d, Failure Rate: %f\n",
               comb->nodes[i]->id, comb->nodes[i]->storage_size, comb->nodes[i]->write_bandwidth,
               comb->nodes[i]->read_bandwidth, comb->nodes[i]->probability_failure);
    }
}

/** Version with approximation **/
// Function to calculate Poisson-Binomial CDF approximation
// This is a simplified version. For accurate calculation, consider using libraries or more complex methods.
double poibin_cdf_approximation(int N, int K, double sum_reliability, double variance_reliability) {
    double cdf = 0.0;
    int n = N - K;
    double mean = sum_reliability / N;
    double stddev = sqrt(variance_reliability);
    double z = (n - mean) / stddev;
    cdf = 0.5 * (1 + erf(z / sqrt(2.0))); // Using error function approximation

    return cdf;
}
// Function to check if the reliability threshold is met
bool reliability_thresold_met_approximation(int N, int K, double reliability_threshold, double sum_reliability, double variance_reliability) {
    double cdf = poibin_cdf_approximation(N, K, sum_reliability, variance_reliability);
    return cdf >= reliability_threshold;
}

/** Version accurate **/
// Initialize PoiBin structure
PoiBin *init_poi_bin_accurate(double *probabilities, int n) {
    PoiBin *pb = (PoiBin *)malloc(sizeof(PoiBin));
    pb->probabilities = (double *)malloc(n * sizeof(double));
    pb->n = n;

    for (int i = 0; i < n; i++) {
        pb->probabilities[i] = probabilities[i];
    }

    return pb;
}
// Compute the PMF for the Poisson-Binomial distribution
double pmf_poi_bin_accurate(PoiBin *pb, int k) {
    //~ double *dp = (double *)calloc(k + 1, sizeof(double));
    //~ dp[0] = 1.0;
    
    double *dp = (double *)malloc((k + 1) * sizeof(double));
    if (dp == NULL) {
        // Handle memory allocation failure
        return -1;  // Or some other error code
    }
    for (int i = 0; i <= k; i++) {
        dp[i] = 0.0;
    }
    dp[0] = 1.0;

    for (int i = 0; i < pb->n; i++) {
        for (int j = k; j > 0; j--) {
            dp[j] = dp[j] * (1 - pb->probabilities[i]) + dp[j - 1] * pb->probabilities[i];
        }
        dp[0] *= (1 - pb->probabilities[i]);
    }

    double result = dp[k];
    free(dp);
    return result;
}
// Compute the CDF for the Poisson-Binomial distribution
double cdf_poi_bin_accurate(PoiBin *pb, int k) {
    double cdf = 0.0;
    for (int i = 0; i <= k; i++) {
        cdf += pmf_poi_bin_accurate(pb, i);
    }
    return cdf;
}
// Free memory allocated for PoiBin
void free_poi_bin_accurate(PoiBin *pb) {
    free(pb->probabilities);
    free(pb);
}
// Check if reliability threshold is met
int reliability_threshold_met_accurate(int N, int K, double reliability_threshold, double *reliability_of_nodes) {
    PoiBin *pb = init_poi_bin_accurate(reliability_of_nodes, N);
    double cdf_value = cdf_poi_bin_accurate(pb, N - K);
    free_poi_bin_accurate(pb);
    return cdf_value >= reliability_threshold;
}

int get_max_K_from_reliability_threshold_and_nodes_chosen(int number_of_nodes, float reliability_threshold, double sum_reliability, double variance_reliability, double* reliability_of_nodes) {
    int K;
    for (int i = number_of_nodes - 1; i >= 2; i--) {
        K = i;
        //~ if (reliability_thresold_met_approximation(number_of_nodes, K, reliability_threshold, sum_reliability, variance_reliability)) {
            //~ return K;
        //~ }
        if (reliability_threshold_met_accurate(number_of_nodes, K, reliability_threshold, reliability_of_nodes)) {
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

void algorithm4(int number_of_nodes, Node* nodes, float reliability_threshold, double size, double max_node_size, double min_data_size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, Combination **combinations, int total_combinations, double* total_remaining_size, double total_storage_size, int closest_index, RealRecords* records_array, LinearModel* models, LinearModel* models_reconstruct, int nearest_size, DataList* list, int data_id, int max_N, double* total_read_time_parrallelized, double* total_read_time, int decision_value_alg4, double* size_stored) {
    int i = 0;
    int j = 0;
    double chunk_size = 0;
    double one_on_number_of_nodes = 1.0/number_of_nodes;
    bool valid_solution = false;
    bool valid_size = false;
    
    // Heart of the function
    struct timeval start, end;
    gettimeofday(&start, NULL);
    long seconds, useconds;
    
    *N = -1;
    *K = -1;

    // 1. Get system saturation
    double system_saturation = get_system_saturation(number_of_nodes, min_data_size, total_storage_size, *total_remaining_size);    
    #ifdef PRINT
    printf("System saturation = %f\n", system_saturation);
    printf("Data size = %f\n", size);
    #endif
    //~ printf("total_combinations %d\n", total_combinations);
    // 2. Iterates over a range of nodes combination
    for (i = 0; i < total_combinations; i++) {
        if (max_N < combinations[i]->num_elements) { combinations[i]->K = -1; continue; }
        //~ printf("%d\n", combinations[i]->num_elements);
        //~ if (i > 900) {
        //~ exit(1); }
        
        *K = get_max_K_from_reliability_threshold_and_nodes_chosen(combinations[i]->num_elements, reliability_threshold, combinations[i]->sum_reliability, combinations[i]->variance_reliability, combinations[i]->probability_failure);
        
        // Reset from last expe the values used in pareto front
        combinations[i]->storage_overhead = 0.0;
        combinations[i]->size_score = 0.0;
        combinations[i]->replication_and_write_time = 0.0;
        combinations[i]->transfer_time_parralelized = 0.0;
        combinations[i]->chunking_time = 0.0;

        #ifdef PRINT
        printf("Max K for combination %d is %d\n", i, *K);
        #endif
        
        combinations[i]->K = *K;
        
        if (*K != -1) {
            chunk_size = size/(*K);
            #ifdef PRINT
            printf("Chunk size from %f and %d: %f\n", size, *K, chunk_size);
            #endif
            
            valid_size = true;
            for (j = 0; j < combinations[i]->num_elements; j++) {
                if (combinations[i]->nodes[j]->storage_size - chunk_size < 0) {
                    valid_size = false;
                    break;
                }
            }
            //~ if (combinations[i]->min_remaining_size - chunk_size >= 0) {
            if (valid_size == true) {
                //~ printf("%d is valid\n", i);
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
                //~ combinations[i]->transfer_time_parralelized = calculate_transfer_time(chunk_size, combinations[i]->min_write_bandwidth);
                combinations[i]->transfer_time_parralelized = fmax(size/out_going_bandwidth, chunk_size/combinations[i]->min_write_bandwidth);
                
                // Ajout du read and reconstruct
                combinations[i]->read_time_parralelized = fmax(size/out_going_bandwidth, chunk_size/combinations[i]->min_read_bandwidth);
                combinations[i]->reconstruct_time = predict_reconstruct(models_reconstruct[closest_index], combinations[i]->num_elements, *K, nearest_size, size);

                combinations[i]->replication_and_write_time = combinations[i]->chunking_time + combinations[i]->transfer_time_parralelized + combinations[i]->read_time_parralelized + combinations[i]->reconstruct_time;
                
                
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
        double total_progress_storage_overhead = max_storage_overhead - min_storage_overhead;
        double total_progress_size_score = max_size_score - min_size_score;
        double total_progress_replication_and_write_time = max_replication_and_write_time - min_replication_and_write_time;
        //~ printf("max_replication_and_write_time %f, min_replication_and_write_time %f", max_replication_and_write_time, min_replication_and_write_time);
        #ifdef PRINT
        printf("Progresses are %f %f %f\n", total_progress_storage_overhead, total_progress_size_score, total_progress_replication_and_write_time);
        #endif
        double time_score = 0;
        double space_score = 0;
        double sat_score = 0;
        double total_score = 0;
        double max_score = -DBL_MAX;
        int idx = 0;
        
        if(isinf(total_progress_replication_and_write_time)) {
            total_progress_replication_and_write_time = 0;
        }
        
        int best_index = -1;
        
        // Getting combination with best score using pareto front progress
        for (i = 0; i < pareto_count; i++) {
            idx = pareto_indices[i];
            if (total_progress_replication_and_write_time > 0) {  // In some cases, when there are not enough solution or if they are similar the total progress is 0. As we don't want to divide by 0, we keep the score at 0 for the corresponding value as no progress could be made
                time_score = 100 - ((combinations[idx]->replication_and_write_time - min_replication_and_write_time)*100)/total_progress_replication_and_write_time;
            }
            
            if (total_progress_storage_overhead > 0) {
                space_score = 100 - ((combinations[idx]->storage_overhead - min_storage_overhead)*100)/total_progress_storage_overhead;
                //~ printf(" / space_score 1 %f", space_score);
            }
            if (total_progress_size_score > 0) {
                sat_score = 100 - ((combinations[idx]->size_score - min_size_score)*100)/total_progress_size_score;
                //~ printf(" / sat_score %f", sat_score);
            }

            if (decision_value_alg4 == 0) {
                // first idea
                total_score = time_score + ((space_score+sat_score)/2.0)*system_saturation;
            }
            else if (decision_value_alg4 == 1) {
                // alternative idea
                total_score = (1 - system_saturation)*time_score + (space_score + sat_score)/2.0;
            }
            else if (decision_value_alg4 == 2) {
                // alternative idea
                total_score = (time_score + space_score)/2 + sat_score;
            }
            else if (decision_value_alg4 == 3) {
                // alternative idea
                total_score = (time_score + space_score)/2 + sat_score*system_saturation;
            }
            //~ printf(" = total_score %f\n", total_score);
            
            if (max_score < total_score) { // Higher score the better
                max_score = total_score;
                best_index = idx;
            }
        }
        
        if (decision_value_alg4 == 4) {
            // Getting combination with best score using 3D pareto knee bend angle max
            // TODO if we keep this no need to compute system saturation
            double knee_point[3];
            #ifdef PRINT
            printf("max_time_index %d, max_saturation_index %d pareto_count %d\n", max_time_index, max_saturation_index, pareto_count);
            #endif
            if (pareto_count == 1) {
                best_index = pareto_indices[0];
            }
            else {
                best_index = pareto_indices[find_knee_point_3d(pareto_front, pareto_count, knee_point, max_time_index, max_saturation_index)];
            }
            #ifdef PRINT
            printf("Knee Point: %d (%.2f, %.2f, %.2f)\n", best_index, knee_point[0], knee_point[1], knee_point[2]);
            printf("Best index is %d with N%d K%d\n", best_index, combinations[best_index]->num_elements, combinations[best_index]->K);
            printf("..\n");
            #endif
        }

        *N = combinations[best_index]->num_elements;
        *K = combinations[best_index]->K;
        gettimeofday(&end, NULL);
        //~ printf("N = %d\n", *N);
        double total_upload_time_to_print = 0;
        
        /** Read **/
        double total_read_time_to_print = 0;
        double total_read_time_parralelized_to_print = 0;
        double reconstruct_time = 0;
        
        // Writing down the results
        if (*N != -1 && *K != -1) {
            chunk_size = size/(*K);
            //~ printf("%f, %f, %d, %d, ", size, chunk_size, *N, *K);
            *number_of_data_stored += 1;
            *total_N += *N;
            *total_storage_used += chunk_size*(*N);
            *total_remaining_size -= chunk_size*(*N);
            //~ *total_parralelized_upload_time += chunk_size/combinations[best_index]->min_write_bandwidth;
            *total_parralelized_upload_time += fmax(size/out_going_bandwidth, chunk_size/combinations[best_index]->min_write_bandwidth);
            *size_stored += size;
            
            /** Read **/
            //~ total_read_time_parralelized_to_print = chunk_size/combinations[best_index]->min_read_bandwidth;
            total_read_time_parralelized_to_print = fmax(chunk_size/combinations[best_index]->min_read_bandwidth, size/out_going_bandwidth);
            reconstruct_time = predict_reconstruct(models_reconstruct[closest_index], *N, *K, nearest_size, size);
            
            int* used_combinations = malloc(*N * sizeof(int));
            
            for (i = 0; i < combinations[best_index]->num_elements; i++) {
                //~ printf("%d ", combinations[best_index]->nodes[i]->id);
                total_upload_time_to_print += chunk_size/combinations[best_index]->nodes[i]->write_bandwidth;
                
                /** Read **/
                total_read_time_to_print += chunk_size/combinations[best_index]->nodes[i]->read_bandwidth;
                
                if (combinations[best_index]->nodes[i]->storage_size - chunk_size < 0) {
                    printf("Error node %d memory %f chunk size %f K %d best_index %d\n", combinations[best_index]->nodes[i]->id, combinations[best_index]->nodes[i]->storage_size, chunk_size, *K, best_index);
                    exit(1);
                }

                combinations[best_index]->nodes[i]->storage_size -= chunk_size;
                
                used_combinations[i] = combinations[best_index]->nodes[i]->id;
            }
            //~ printf("\n");
            
            // Adding the chunks in the chosen nodes ids
            add_shared_chunks_to_nodes(used_combinations, combinations[best_index]->num_elements, data_id, chunk_size, nodes,  number_of_nodes, size);
            
            /** Read **/
            //~ printf("%f N%d K%d %f\n", combinations[best_index]->chunking_time, *N, *K, reconstruct_time);
            
            add_node_to_print(list, data_id, size, total_upload_time_to_print, combinations[best_index]->transfer_time_parralelized, combinations[best_index]->chunking_time, *N, *K, total_read_time_to_print, total_read_time_parralelized_to_print, reconstruct_time);
            
            *total_upload_time += total_upload_time_to_print;
           
            /** Read **/
            *total_read_time_parrallelized += total_read_time_parralelized_to_print;
            *total_read_time += total_read_time_to_print;
            
            free(used_combinations);
        }
    }
    else {
        gettimeofday(&end, NULL);
    }
    seconds  = end.tv_sec  - start.tv_sec;
    useconds = end.tv_usec - start.tv_usec;
    *total_scheduling_time += seconds + useconds/1000000.0;
}

void algorithm2(int number_of_nodes, Node* nodes, float reliability_threshold, double size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, Combination **combinations, int total_combinations, double total_storage_size, int closest_index, RealRecords* records_array, LinearModel* models, LinearModel* models_reconstruct, int nearest_size, DataList* list, int data_id, int max_N, double* total_read_time_parrallelized, double* total_read_time, double* size_stored) {
    int i = 0;
    int j = 0;
    double chunk_size = 0;
    bool valid_solution = false;
    bool valid_size = false;
    
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
        if (max_N < combinations[i]->num_elements) { continue; }
        *K = get_max_K_from_reliability_threshold_and_nodes_chosen(combinations[i]->num_elements, reliability_threshold, combinations[i]->sum_reliability, combinations[i]->variance_reliability, combinations[i]->probability_failure);
        #ifdef PRINT
        printf("Max K for combination %d is %d\n", i, *K);
        #endif
        
        // Reset from last expe the values used in pareto front
        combinations[i]->total_transfer_time = 0.0;
        combinations[i]->chunking_time = 0.0;
        combinations[i]->K = *K;
        
        if (*K != -1) {
            chunk_size = size/(*K);
            
            valid_size = true;
            for (j = 0; j < combinations[i]->num_elements; j++) {
                if (combinations[i]->nodes[j]->storage_size - chunk_size < 0) {
                    valid_size = false;
                    break;
                }
            }

            if (valid_size == true) {                
                
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
        
        /** Read **/
        double total_read_time_to_print = 0;
        double total_read_time_parralelized_to_print = 0;
        double reconstruct_time = 0;
        
        // Writing down the results
        if (*N != -1 && *K != -1) {
            chunk_size = size/(*K);
            
            /** Read **/
            total_read_time_parralelized_to_print = chunk_size/combinations[best_index]->min_read_bandwidth;
            reconstruct_time = predict_reconstruct(models_reconstruct[closest_index], *N, *K, nearest_size, size);
            
            *number_of_data_stored += 1;
            *total_N += *N;
            *total_storage_used += chunk_size*(*N);
            //~ *total_parralelized_upload_time += chunk_size/combinations[best_index]->min_write_bandwidth;
            *total_parralelized_upload_time += fmax(size/out_going_bandwidth, chunk_size/combinations[best_index]->min_write_bandwidth);
            *size_stored += size;
            
            int* used_combinations = malloc(*N * sizeof(int));
            
            for (i = 0; i < combinations[best_index]->num_elements; i++) {
                total_upload_time_to_print += chunk_size/combinations[best_index]->nodes[i]->write_bandwidth;
                
                /** Read **/
                total_read_time_to_print += chunk_size/combinations[best_index]->nodes[i]->read_bandwidth;
                
                combinations[best_index]->nodes[i]->storage_size -= chunk_size;  
                
                used_combinations[i] = combinations[best_index]->nodes[i]->id;              
            }
            
            // Adding the chunks in the chosen nodes
            add_shared_chunks_to_nodes(used_combinations, combinations[best_index]->num_elements, data_id, chunk_size, nodes,  number_of_nodes, size);

            add_node_to_print(list, data_id, size, total_upload_time_to_print, combinations[best_index]->transfer_time_parralelized, combinations[best_index]->chunking_time, *N, *K, total_read_time_to_print, total_read_time_parralelized_to_print, reconstruct_time);
            *total_upload_time += total_upload_time_to_print;
            
            /** Read **/
            *total_read_time_parrallelized += total_read_time_parralelized_to_print;
            *total_read_time += total_read_time_to_print;
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
        printf("Error opening file %s", filename);
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

//~ void find_closest_reconstruct(int target, int* nearest_size, int* closest_index) {
    //~ // The array of numbers to compare against
    //~ int numbers[] = {1, 10, 100, 400};
    //~ int size = sizeof(numbers) / sizeof(numbers[0]);

    //~ // Initialize the closest number to the first element
    //~ int min_diff = abs(target - numbers[0]);

    //~ // Iterate over the array to find the closest number
    //~ for (int i = 1; i < size; i++) {
        //~ int diff = abs(target - numbers[i]);
        //~ if (diff < min_diff) {
            //~ min_diff = diff;
            //~ *nearest_size = numbers[i];
            //~ *closest_index = i;
        //~ }
    //~ }
//~ }

/** Comparison function for sorting nodes by remaining storage size in descending order
 * Nodes with add_after_x_jobs > current_data_value or add_after_x_jobs == -1 are sorted to the end **/
int compare_nodes_by_storage_desc_with_condition(const void *a, const void *b) {
    Node *nodeA = (Node *)a;
    Node *nodeB = (Node *)b;

    // Handle nodes with add_after_x_jobs == -1 first
    if (nodeA->add_after_x_jobs == -1 && nodeB->add_after_x_jobs != -1) {
        return 1; // Move nodeA to the end
    }
    if (nodeA->add_after_x_jobs != -1 && nodeB->add_after_x_jobs == -1) {
        return -1; // Move nodeB to the end
    }
    
    // Check if the nodes should be moved to the end
    if (nodeA->add_after_x_jobs > global_current_data_value && nodeB->add_after_x_jobs <= global_current_data_value) {
        return 1; // Move nodeA to the end
    }
    if (nodeA->add_after_x_jobs <= global_current_data_value && nodeB->add_after_x_jobs > global_current_data_value) {
        return -1; // Move nodeB to the end
    }

    // If both nodes are in the same category (both above or below the threshold)
    if (nodeA->storage_size < nodeB->storage_size) return 1;
    if (nodeA->storage_size > nodeB->storage_size) return -1;

    return 0;
}

/** Comparison function for sorting nodes by remaining storage size in descending order
 * Nodes with add_after_x_jobs > current_data_value or add_after_x_jobs == -1 are sorted to the end **/
int compare_nodes_by_reliability_desc_with_condition(const void *a, const void *b) {
    Node *nodeA = (Node *)a;
    Node *nodeB = (Node *)b;

    // Handle nodes with add_after_x_jobs == -1 first
    if (nodeA->add_after_x_jobs == -1 && nodeB->add_after_x_jobs != -1) {
        return 1; // Move nodeA to the end
    }
    if (nodeA->add_after_x_jobs != -1 && nodeB->add_after_x_jobs == -1) {
        return -1; // Move nodeB to the end
    }
    
    // Check if the nodes should be moved to the end
    if (nodeA->add_after_x_jobs > global_current_data_value && nodeB->add_after_x_jobs <= global_current_data_value) {
        return 1; // Move nodeA to the end
    }
    if (nodeA->add_after_x_jobs <= global_current_data_value && nodeB->add_after_x_jobs > global_current_data_value) {
        return -1; // Move nodeB to the end
    }

    // If both nodes are in the same category (both above or below the threshold)
    if (nodeA->probability_failure > nodeB->probability_failure) return 1;
    if (nodeA->probability_failure < nodeB->probability_failure) return -1;

    return 0;
}

/** Comparison function for sorting nodes by bandwidth in descending order
 * Nodes with add_after_x_jobs > current_data_value or add_after_x_jobs == -1 are sorted to the end **/
int compare_nodes_by_bandwidth_desc_with_condition(const void *a, const void *b) {
    Node *nodeA = (Node *)a;
    Node *nodeB = (Node *)b;

    // Handle nodes with add_after_x_jobs == -1 first
    if (nodeA->add_after_x_jobs == -1 && nodeB->add_after_x_jobs != -1) {
        return 1; // Move nodeA to the end
    }
    if (nodeA->add_after_x_jobs != -1 && nodeB->add_after_x_jobs == -1) {
        return -1; // Move nodeB to the end
    }
    
    // Check if the nodes should be moved to the end
    if (nodeA->add_after_x_jobs > global_current_data_value && nodeB->add_after_x_jobs <= global_current_data_value) {
        return 1; // Move nodeA to the end
    }
    if (nodeA->add_after_x_jobs <= global_current_data_value && nodeB->add_after_x_jobs > global_current_data_value) {
        return -1; // Move nodeB to the end
    }

    // If both nodes are in the same category (both above or below the threshold)
    if (nodeA->write_bandwidth < nodeB->write_bandwidth) return 1;
    if (nodeA->write_bandwidth > nodeB->write_bandwidth) return -1;

    return 0;
}

/** Comparison function for sorting nodes by bandwidth in descending order
 * Nodes with add_after_x_jobs > current_data_value or add_after_x_jobs == -1 are sorted to the end **/
int compare_nodes_by_read_bandwidth_desc_with_condition(const void *a, const void *b) {
    Node *nodeA = (Node *)a;
    Node *nodeB = (Node *)b;

    // Handle nodes with add_after_x_jobs == -1 first
    if (nodeA->add_after_x_jobs == -1 && nodeB->add_after_x_jobs != -1) {
        return 1; // Move nodeA to the end
    }
    if (nodeA->add_after_x_jobs != -1 && nodeB->add_after_x_jobs == -1) {
        return -1; // Move nodeB to the end
    }
    
    // Check if the nodes should be moved to the end
    if (nodeA->add_after_x_jobs > global_current_data_value && nodeB->add_after_x_jobs <= global_current_data_value) {
        return 1; // Move nodeA to the end
    }
    if (nodeA->add_after_x_jobs <= global_current_data_value && nodeB->add_after_x_jobs > global_current_data_value) {
        return -1; // Move nodeB to the end
    }

    // If both nodes are in the same category (both above or below the threshold)
    if (nodeA->read_bandwidth < nodeB->read_bandwidth) return 1;
    if (nodeA->read_bandwidth > nodeB->read_bandwidth) return -1;

    return 0;
}

/** Comparison function for sorting nodes by (write_bandwidth + read_bandwidth) in descending order
 * Nodes with add_after_x_jobs > current_data_value or add_after_x_jobs == -1 are sorted to the end **/
int compare_nodes_by_bandwidth_read_and_write_desc_with_condition(const void *a, const void *b) {
    Node *nodeA = (Node *)a;
    Node *nodeB = (Node *)b;

    // Handle nodes with add_after_x_jobs == -1 first
    if (nodeA->add_after_x_jobs == -1 && nodeB->add_after_x_jobs != -1) {
        return 1; // Move nodeA to the end
    }
    if (nodeA->add_after_x_jobs != -1 && nodeB->add_after_x_jobs == -1) {
        return -1; // Move nodeB to the end
    }
    
    // Check if the nodes should be moved to the end
    if (nodeA->add_after_x_jobs > global_current_data_value && nodeB->add_after_x_jobs <= global_current_data_value) {
        return 1; // Move nodeA to the end
    }
    if (nodeA->add_after_x_jobs <= global_current_data_value && nodeB->add_after_x_jobs > global_current_data_value) {
        return -1; // Move nodeB to the end
    }

    // Compare by the sum of write_bandwidth and read_bandwidth
    int bandwidthA = nodeA->write_bandwidth + nodeA->read_bandwidth;
    int bandwidthB = nodeB->write_bandwidth + nodeB->read_bandwidth;

    if (bandwidthA < bandwidthB) return 1;
    if (bandwidthA > bandwidthB) return -1;

    return 0;
}

// Function to print nodes
void print_nodes(Node *nodes, int num_nodes) {
    for (int i = 0; i < num_nodes; i++) {
        printf("Node %d: Storage Size = %.2f, Write Bandwidth = %d, Read Bandwidth = %d, Failure Rate = %.2f, %d\n",
               nodes[i].id, nodes[i].storage_size, nodes[i].write_bandwidth, nodes[i].read_bandwidth, nodes[i].probability_failure, nodes[i].add_after_x_jobs);
    }
}

int main(int argc, char *argv[]) {
    int i = 0;
    int j = 0;
    int k = 0;
    if (argc < 11) {
        fprintf(stderr, "Usage: %s <input_node> <input_data> <data_duration_on_system> <reliability_threshold> <number_of_repetition> <algorithm> <input_supplementary_node> <remove_node_pattern> <fixed_random_seed> <max_N>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *input_node = argv[1];
    const char *input_data = argv[2];
    double data_duration_on_system = atof(argv[3]);
    double reliability_threshold = atof(argv[4]);
    int number_of_repetition = atoi(argv[5]);
    int algorithm = atoi(argv[6]); // 0: random / 1: min_storage / 2: min_time / 3: hdfs_3_replication / 4: drex / 5: Bogdan / 6: hdfs_rs / 7: glusterfs
    const char *input_supplementary_node = argv[7];
    
    //~ printf("data_size, chunk_size, N, K, chosen_nodes\n");
        
    // For the removal of nodes
    int remove_node_pattern = atoi(argv[8]); // 0 for no removal, 1 for removal randomly, 2 for following failure rate
    unsigned int seed = atoi(argv[9]);  // We fix the seed so all algorithm have the same one
    srand(seed); // Set the seed up
    int max_N_arg = atoi(argv[10]); // 0 if no max_N, otherwise if we set up a max_N
    const char *remove_node_pattern_file = NULL;
    if (remove_node_pattern == 3) { remove_node_pattern_file = argv[11]; }
    //~ double fixed_throughput = atof(argv[12]);
    
    // For certain algorithms there are additional args
    int RS1;
    int RS2;
    if (algorithm == 6 || algorithm == 7 || algorithm == 8) {
        RS1 = atoi(argv[12]);
        RS2 = atoi(argv[13]);
    }
    int decision_value_alg4 = 0;
    if (algorithm == 4) {
        decision_value_alg4 = atoi(argv[12]);
    }
    
    //~ printf("Algorithm %d. Data have to stay %f days on the system. Reliability threshold is %.9f. Number of repetition is %d. Remove node pattern is %d. Seed is %d. Max_N is %d.\n", algorithm, data_duration_on_system, reliability_threshold, number_of_repetition, remove_node_pattern, seed, max_N_arg);
    
    DataList list;
    init_list(&list);
    TimeList list_time;
    init_list_time(&list_time);
    
    // Step 1: Count the number of lines
    int count = count_lines_with_access_type(input_data);
    count = count*number_of_repetition;
    int number_of_initial_nodes = count_nodes(input_node);
    int number_of_supplementary_nodes = count_nodes(input_supplementary_node);
    int number_of_nodes = number_of_initial_nodes + number_of_supplementary_nodes;
    //~ printf("number_of_initial_nodes: %d", number_of_initial_nodes);
    //~ printf(" / number_of_supplementary_nodes: %d", number_of_supplementary_nodes);
    //~ printf(" / number_of_nodes: %d\n", number_of_nodes);
    
    // Step 2: Allocate memory
    double *sizes = (double*)malloc(count * sizeof(double));
    int *submit_times = (int*)malloc(count * sizeof(int));
    double *target_reliability = (double*)malloc(count * sizeof(double));
    if (sizes == NULL || submit_times == NULL) {
        perror("Error allocating memory");
        return EXIT_FAILURE;
    }
    Node *nodes = (Node *)malloc(number_of_nodes * sizeof(Node));
    if (nodes == NULL) {
        perror("Error allocating memory");
        return EXIT_FAILURE;
    }

    // Step 3: Read data into the arrays
    read_data(input_data, sizes, submit_times, number_of_repetition, target_reliability);
    double total_storage_size = 0;
    double max_node_size = 0;
    double *initial_node_sizes = (double*)malloc(number_of_nodes * sizeof(double));
    read_node(input_node, number_of_initial_nodes, nodes, data_duration_on_system, &max_node_size, &total_storage_size, initial_node_sizes);
    int* supplementary_nodes_next_time = malloc(number_of_supplementary_nodes*sizeof(int));
    double* total_storage_supplementary_nodes = malloc(number_of_supplementary_nodes*sizeof(double));
    double* max_node_size_supplementary_nodes = malloc(number_of_supplementary_nodes*sizeof(double));
    if (number_of_supplementary_nodes > 0) {
        read_supplementary_node(input_supplementary_node, number_of_supplementary_nodes, nodes, data_duration_on_system, initial_node_sizes, number_of_initial_nodes, supplementary_nodes_next_time, total_storage_supplementary_nodes, max_node_size_supplementary_nodes);
    }
    
    // Print the collected data
    #ifdef PRINT
    printf("There are %d data in W mode:\n", count);
    for (i = 0; i < count; i++) {
        printf("%.2f %d\n", sizes[i], submit_times[i]);
    }
    #endif
    
    #ifdef PRINT
    for (i = 0; i < number_of_nodes; i++) {
        printf("Node %d: storage_size=%f, write_bandwidth=%d, read_bandwidth=%d, probability_failure=%f\n",
               nodes[i].id, nodes[i].storage_size, nodes[i].write_bandwidth,
               nodes[i].read_bandwidth, nodes[i].probability_failure);
        //~ printf("initial_node_sizes %d: %f\n", i, initial_node_sizes[i]);
    }
    printf("Max node size is %f\n", max_node_size);
    printf("Total storage size is %f\n", total_storage_size);
    #endif
    
    // Variables used in algorithm4
    double min_data_size = DBL_MAX;
    int N;
    int K;
    const char *output_filename = "output_drex_only.csv";
    bool is_daos = false;
    
    char alg_to_print[50];
    if (algorithm == 4) {
        sprintf(alg_to_print, "alg4_%d", decision_value_alg4);
    }
    else if (algorithm == 2) {
        strcpy(alg_to_print, "alg2");
    }
    else if (algorithm == 5) {
        strcpy(alg_to_print, "alg_bogdan");
    }
    else if (algorithm == 1) {
        strcpy(alg_to_print, "alg1_c");
    }
    else if (algorithm == 10) {
        strcpy(alg_to_print, "least_used_node");
    }
    else if (algorithm == 9) {
        strcpy(alg_to_print, "optimal_schedule");
    }
    else if (algorithm == 0) {
        strcpy(alg_to_print, "random_c");
    }
    else if (algorithm == 3) {
        strcpy(alg_to_print, "hdfs_3_replication_c");
    }
    else if (algorithm == 6) {
        sprintf(alg_to_print, "hdfs_rs_%d_%d_c", RS1, RS2);
    }
    else if (algorithm == 7) {
        sprintf(alg_to_print, "glusterfs_%d_%d_c", RS1, RS2);
    }
    else if (algorithm == 8) {
        sprintf(alg_to_print, "daos_%d_%d_c", RS1, RS2);
        is_daos = true;
    }
    double total_scheduling_time = 0;
    double total_storage_used = 0;
    double size_stored = 0;
    double total_upload_time = 0;
    double total_parralelized_upload_time = 0;
    double total_read_time = 0;
    double total_read_time_parrallelized = 0;
    int number_of_data_stored = 0;
    int total_N = 0; // Number of chunks
    
    
    /** Building combinations **/
    Combination **combinations = NULL;
    // Calculate total number of combinations
    int total_combinations = 0;
    int combination_count = 0;
    bool reduced_complexity_situation;
    int min_number_node_in_combination = 2;
    //~ unsigned long long complexity_threshold = 2000;
    unsigned long long complexity_threshold = 1025;
    int max_number_node_in_combination = number_of_initial_nodes;
    for (i = min_number_node_in_combination; i <= max_number_node_in_combination; i++) {
        total_combinations += combination(number_of_initial_nodes, i, complexity_threshold);
    }
    #ifdef PRINT
    printf("There are %d possible combinations\n", total_combinations);
    #endif
    int max_number_combination_per_r = 0;
    global_current_data_value = 0;
    
    // Sort nodes by remaining storage size
    qsort(nodes, number_of_initial_nodes, sizeof(Node), compare_nodes_by_storage_desc_with_condition);
    //~ print_nodes(nodes, number_of_initial_nodes);
    
    if (total_combinations >= complexity_threshold) {
        reduced_complexity_situation = true;
        // Assign max number of combination per number of node in a combination
        max_number_combination_per_r = complexity_threshold/(number_of_initial_nodes - 1);
        
        // Sort nodes by remaining storage size
        //~ qsort(nodes, number_of_initial_nodes, sizeof(Node), compare_nodes_by_storage);
        qsort(nodes, number_of_initial_nodes, sizeof(Node), compare_nodes_by_storage_desc_with_condition);
        //~ print_nodes(nodes, number_of_initial_nodes);
        
        // Alloc the combinations
        combinations = malloc(complexity_threshold * sizeof(Combination *));
        
        // create combinations but stop when limit is reached
        for (i = min_number_node_in_combination; i <= max_number_node_in_combination; i++) {
            create_combinations_with_limit(nodes, number_of_initial_nodes, i, combinations, &combination_count, max_number_combination_per_r);
        }
        
        total_combinations = combination_count;
    }
    else {
        reduced_complexity_situation = false;
        // Allocate memory for storing all combinations
        combinations = malloc(total_combinations * sizeof(Combination *));
        if (combinations == NULL) {
            perror("Error allocating memory for combinations");
            exit(EXIT_FAILURE);
        }
        for (i = min_number_node_in_combination; i <= max_number_node_in_combination; i++) {
            create_combinations(nodes, number_of_initial_nodes, i, combinations, &combination_count);
        }
    }
    
    #ifdef PRINT
    for (i = 0; i < total_combinations; i++) {
        printf("Combination %d: ", i + 1);
        for (j = 0; j < combinations[i]->num_elements; j++) {
            printf("%d ", combinations[i]->nodes[j]->id);
            printf("(%d) - ", combinations[i]->write_bandwidth[j]);
        }
        printf("\n");
    }
    #endif      
    
    /** Prediction of chunking  and reconstruct time **/
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
    //~ int num_files_reconstruct = 4;
    int num_files_reconstruct = 6;
    const char *filenames_reconstruct[] = {
        "data/reconstruct/new_c/1MB.csv", 
        "data/reconstruct/new_c/10MB.csv", 
        "data/reconstruct/new_c/50MB.csv",
        "data/reconstruct/new_c/100MB.csv",
        "data/reconstruct/new_c/200MB.csv",
        "data/reconstruct/new_c/400MB.csv"
    };
    // Array to hold RealRecords for each file
    RealRecords *records_array = (RealRecords *)malloc(num_files * sizeof(RealRecords));
    RealRecords *records_array_reconstruct = (RealRecords *)malloc(num_files_reconstruct * sizeof(RealRecords));
    if (records_array == NULL || records_array_reconstruct == NULL) {
        perror("Memory allocation failed for records array");
        exit(EXIT_FAILURE);
    }
    // Read records from each file
    for (i = 0; i < num_files; i++) {
        read_records(filenames[i], &records_array[i]);
    }
    for (i = 0; i < num_files_reconstruct; i++) {
        read_records(filenames_reconstruct[i], &records_array_reconstruct[i]);
    }

    // Print the data to verify (example for the first file)
    #ifdef PRINT
    //~ for (i = 0; i < 171; i++) {
        //~ printf("File %s, Row %d: n: %.2f, k: %.2f, avg_time: %.6f\n", filenames[0], i, records_array[0].n[i], records_array[0].k[i], records_array[0].avg_time[i]);
    //~ }
    for (i = 0; i < 171; i++) {
        printf("File %s, Row %d: n: %.2f, k: %.2f, avg_time: %.6f\n", filenames_reconstruct[0], i, records_array_reconstruct[0].n[i], records_array_reconstruct[0].k[i], records_array_reconstruct[0].avg_time[i]);
        printf("File %s, Row %d: n: %.2f, k: %.2f, avg_time: %.6f\n", filenames_reconstruct[3], i, records_array_reconstruct[3].n[i], records_array_reconstruct[3].k[i], records_array_reconstruct[3].avg_time[i]);
        printf("File %s, Row %d: n: %.2f, k: %.2f, avg_time: %.6f\n", filenames_reconstruct[5], i, records_array_reconstruct[5].n[i], records_array_reconstruct[5].k[i], records_array_reconstruct[5].avg_time[i]);
    }
    #endif

    LinearModel *models = (LinearModel *)malloc(num_files * sizeof(LinearModel));
    LinearModel *models_reconstruct = (LinearModel *)malloc(num_files_reconstruct * sizeof(LinearModel));
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
    for (i = 0; i < num_files_reconstruct; i++) {
        c0 = 0;
        c1 = 0;
        c2 = 0;
        if (fit_linear_model(&records_array_reconstruct[i], &c0, &c1, &c2) == 0) {
            #ifdef PRINT
            printf("Fitted coefficients_reconstruct for i=%d: c0 = %f, c1 = %f, c2 = %f\n", i, c0, c1, c2);
            #endif
        } else {
            fprintf(stderr, "Failed to fit linear model.\n");
        }
        models_reconstruct[i].intercept = c0;
        models_reconstruct[i].slope_n = c1;
        models_reconstruct[i].slope_k = c2;
    }

    double total_remaining_size = total_storage_size; // Used for system saturation
    int closest_index = 0;
    int nearest_size = 0;
    int removed_node_index;
    // Current number of nodes being used. Will be updated when next node time is reached
    int current_number_of_nodes = number_of_initial_nodes;
    double input_data_sum_of_size_already_stored = 0;
    int next_node_to_add_index = 0;
    
    int max_N = 0;
    if (max_N_arg == 0) { // max_N is just the number of nodes if we don't use it
        max_N = current_number_of_nodes;
    }
    
    double best_upload_time_to_print = 0;
    double best_read_time_to_print = 0;
    
    //~ printf("total_storage_size = %f\n", total_storage_size);
    int removed_node_id = -1;
    //~ double* data_to_replicate = NULL;
    int number_of_data_to_replicate_after_loss = 0;
    int total_number_of_data_to_replicate_after_loss = 0;
    double data_to_store = 0;
    int data_to_store_id = 0;
    double* data_to_replicate = NULL;
    
    int last_submit_time_used = 0; // Indicate the time ofthe last submitted task in order to update the random node removal using time and not number of jobs submissions
    
    /** Print time of failure of all nodes **/
    //~ int number_of_day_elapsed = 0;
    //~ number_of_day_elapsed = submit_times[count - 1]/86400;
    //~ for (i = 0; i < number_of_day_elapsed; i++) {
        //~ for (j = 0; j < number_of_nodes; j++) {
            //~ if (check_if_node_failed(&nodes[j])) {
                //~ printf("Node %d failed at day %d time %d\n", nodes[j].id, i, i*86400);
            //~ }
        //~ }
    //~ } exit(1);
    
    /** Fill tab for remove times **/
    int tab[number_of_nodes];
    if (remove_node_pattern == 3) {
        FILE *file = fopen(remove_node_pattern_file, "r");
        if (file == NULL) {
            printf("Error: Could not open file %s.\n", remove_node_pattern_file);
            return 1;
        }
        for (i = 0; i < number_of_nodes; i++) {
            tab[i] = -1;
        }
        int id;
        int failed_time;
        char line[100]; // Buffer to read lines
        fgets(line, sizeof(line), file);
        while (fgets(line, sizeof(line), file)) {
            if (sscanf(line, "%d,%d", &id, &failed_time) == 2) {
                if (id >= 0 && id < number_of_nodes) {
                    tab[id] = failed_time;
                }
            }
        }
        fclose(file);
        printf("Node failures:\n");
        for (i = 0; i < number_of_nodes; i++) {
            printf("Node %d: %d\n", i, tab[i]);
        }
    }
    double current_target_reliability = reliability_threshold;
    if (reliability_threshold == -1 && remove_node_pattern != 0) {
        printf("ERROR: reliability_threshold == -1 && node_removal_pattern != 0 not dealt with\n");
        exit(1);
    }
    
    /** Simulation main loop **/
    
    printf("data_size, chunk_size, N, K, chosen_nodes\n");
    //~ printf("count: %d\n", count);
    for (i = 0; i < count; i++) {
        
        if (reliability_threshold == -1) {
            current_target_reliability = target_reliability[i];
            //~ printf("current_target_reliability: %f\n", current_target_reliability);
        }
        
        add_time_to_print(&list_time, submit_times[i], size_stored);
       
        //~ if (i%100 == 0) {
        //~ if (i%50000 == 0) {
            //~ printf("Data %d/%d of size %f\n", i, count, sizes[i]);
        //~ }
        
        if (min_data_size > sizes[i]) {
            min_data_size = sizes[i];
        }
                
        /** Adding a node **/
        // If we reached a threshold for a new node, we add it to the list of combinations
        if (number_of_supplementary_nodes > 0 && i == supplementary_nodes_next_time[next_node_to_add_index]) {
            global_current_data_value = i;
            //~ printf("Adding node %d\n", nodes[number_of_initial_nodes + next_node_to_add_index].id);
            current_number_of_nodes += 1;
            
            if (max_N_arg == 0) { // max_N is just the number of nodes if we don't use it
                max_N = current_number_of_nodes;
            }
            
            total_storage_size += total_storage_supplementary_nodes[next_node_to_add_index];
            //~ printf("total_storage_size = %f\n", total_storage_size);
            if (max_node_size < max_node_size_supplementary_nodes[next_node_to_add_index]) {
                max_node_size = max_node_size_supplementary_nodes[next_node_to_add_index];
                //~ printf("New max node size %f\n", max_node_size_supplementary_nodes[next_node_to_add_index]);
            }
            qsort(nodes, number_of_supplementary_nodes + number_of_initial_nodes, sizeof(Node), compare_nodes_by_storage_desc_with_condition);
            total_remaining_size = get_total_remaining_size(nodes, current_number_of_nodes);
            
            if (next_node_to_add_index < number_of_supplementary_nodes - 1) {
                next_node_to_add_index += 1;
            }

            // Version dans une fonction
            if (algorithm == 4 || algorithm == 2) {
                free_combinations(combinations, total_combinations);
                combinations = reset_combinations_and_recreate_them(&total_combinations, min_number_node_in_combination, current_number_of_nodes, complexity_threshold, nodes, i, &reduced_complexity_situation);
            }
        }

        /** Removing a node **/
        if (remove_node_pattern != 0) {
            number_of_data_to_replicate_after_loss = 0;
            global_current_data_value = i;
            if (remove_node_pattern == 1 && i == 10000) { // Remove a node at job 10000 randomly
                removed_node_index = remove_random_node(current_number_of_nodes, nodes, &removed_node_id);
                
                total_storage_size -= initial_node_sizes[removed_node_id];
                //~ printf("total_storage_size = %f\n", total_storage_size);
                
                data_to_replicate = reschedule_lost_chunks(&nodes[removed_node_index], nodes, current_number_of_nodes, &number_of_data_to_replicate_after_loss, algorithm);
                total_number_of_data_to_replicate_after_loss += number_of_data_to_replicate_after_loss;
                current_number_of_nodes -=1;
                                
                if (max_N_arg == 0) { // max_N is just the number of nodes if we don't use it
                    max_N = current_number_of_nodes;
                }
    
                qsort(nodes, number_of_supplementary_nodes + number_of_initial_nodes, sizeof(Node), compare_nodes_by_storage_desc_with_condition);
                total_remaining_size = get_total_remaining_size(nodes, current_number_of_nodes);
            }
            if (remove_node_pattern == 2) {
                for (j = last_submit_time_used; j < submit_times[i]; j++) {
                    number_of_data_to_replicate_after_loss = 0;
                    removed_node_index = remove_node_following_failure_rate(current_number_of_nodes, nodes, &removed_node_id, j);
                    if (removed_node_index != -1) {
                        total_storage_size -= initial_node_sizes[removed_node_id];
                        data_to_replicate = reschedule_lost_chunks(&nodes[removed_node_index], nodes, current_number_of_nodes, &number_of_data_to_replicate_after_loss, algorithm);
                        total_number_of_data_to_replicate_after_loss += number_of_data_to_replicate_after_loss;
                        current_number_of_nodes -=1;
                        if (max_N_arg == 0) { // max_N is just the number of nodes if we don't use it
                            max_N = current_number_of_nodes;
                        }
                        qsort(nodes, number_of_supplementary_nodes + number_of_initial_nodes, sizeof(Node), compare_nodes_by_storage_desc_with_condition);
                        total_remaining_size = get_total_remaining_size(nodes, current_number_of_nodes);
                    }
                    
                    if ((algorithm == 4 || algorithm == 2) && removed_node_index != -1) {
                        free_combinations(combinations, total_combinations); //pb here ?
                        combinations = reset_combinations_and_recreate_them(&total_combinations, min_number_node_in_combination, current_number_of_nodes, complexity_threshold, nodes, i, &reduced_complexity_situation);
                    }
            // Reschedule if I have to
            if (number_of_data_to_replicate_after_loss != 0) {

                for (j = 0; j < number_of_data_to_replicate_after_loss; j++) {
                    data_to_store = data_to_replicate[j];
                    data_to_store_id = count + total_number_of_data_to_replicate_after_loss - number_of_data_to_replicate_after_loss + j;
                    //~ printf("RESCHEDULE new id to reschedule is %d size is %f\n", data_to_store_id, data_to_store);
                    
                    // paste all code from find to print chunks
                    find_closest(data_to_store, &nearest_size, &closest_index);
                    
                    if (algorithm == 0) {
                        random_schedule(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                    }
                    else if (algorithm == 1) {
                        min_storage(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                    }
                    else if (algorithm == 10) {
                        least_used_node(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                    }
                    else if (algorithm == 9) {
                        optimal_schedule(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, combinations, total_combinations, &best_upload_time_to_print, &best_read_time_to_print, &size_stored);
                    }
                    else if (algorithm == 3) {
                        hdfs_3_replications(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                    }
                    else if (algorithm == 6) {
                        hdfs_rs(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, RS1, RS2, &total_read_time_parrallelized, &total_read_time, max_N, &size_stored);
                    }
                    else if (algorithm == 7) {
                        glusterfs(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, RS1, RS2, &total_read_time_parrallelized, &total_read_time, is_daos, max_N, &size_stored);
                    }
                    else if (algorithm == 8) {
                        glusterfs(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, RS1, RS2, &total_read_time_parrallelized, &total_read_time, is_daos, max_N, &size_stored);
                    }
                    else if (algorithm == 2) {
                        algorithm2(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, combinations, total_combinations, total_storage_size, closest_index, records_array, models, models_reconstruct, nearest_size, &list, i, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                    }
                    else if (algorithm == 4) {
                        algorithm4(current_number_of_nodes, nodes, reliability_threshold, data_to_store, max_node_size, min_data_size, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, combinations, total_combinations, &total_remaining_size, total_storage_size, closest_index, records_array, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, decision_value_alg4, &size_stored);
                    }
                    else if (algorithm == 5) {
                        balance_penalty_algorithm(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, &total_remaining_size, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                    }
                    else {
                        printf("Algorithm %d not valid\n", algorithm);
                    }
                    //~ printf("RESCHEDULE Algorithm %d chose N = %d and K = %d\n", algorithm, N, K);
                    if (N > max_N) { printf("error N > max_N\n"); exit(1); }
                                        
                        number_of_data_stored -= 1;
                        size_stored -= data_to_store;
                    
                    //~ print_all_chunks(nodes, current_number_of_nodes);
                    input_data_sum_of_size_already_stored += data_to_store;
                }
                free(data_to_replicate); // TODO yeah do that ? Or set it to null ?
                number_of_data_to_replicate_after_loss = 0;
            }
                }
                last_submit_time_used = submit_times[i];
            }
            if (remove_node_pattern == 3) {
                for (j = 0; j < number_of_initial_nodes; j++) {
                    if (tab[j] != -1 && submit_times[i] >= tab[j]) {
                        tab[j] = -1;
                        //~ printf("Node %d failed at time %d\n", j, submit_times[i]);
                        for (k = 0; k < number_of_initial_nodes; k++) {
                            if (nodes[k].id == j) {
                                nodes[k].add_after_x_jobs = -1;
                                removed_node_index = k;
                                removed_node_id = j;
                                //~ printf("break\n");
                                break;
                            }
                        }
                        total_storage_size -= initial_node_sizes[removed_node_id];
                        data_to_replicate = reschedule_lost_chunks(&nodes[removed_node_index], nodes, current_number_of_nodes, &number_of_data_to_replicate_after_loss, algorithm);
                        //~ printf("la\n");
                        total_number_of_data_to_replicate_after_loss += number_of_data_to_replicate_after_loss;
                        current_number_of_nodes -=1;
                        //~ printf("current_number_of_nodes = %d\n", current_number_of_nodes);
                        if (max_N_arg == 0) {
                            max_N = current_number_of_nodes;
                        }
                        qsort(nodes, number_of_supplementary_nodes + number_of_initial_nodes, sizeof(Node), compare_nodes_by_storage_desc_with_condition);
                        //~ print_nodes(nodes, current_number_of_nodes);
                        total_remaining_size = get_total_remaining_size(nodes, current_number_of_nodes);
                        if (algorithm == 4 || algorithm == 2) {
                            free_combinations(combinations, total_combinations);
                            combinations = reset_combinations_and_recreate_them(&total_combinations, min_number_node_in_combination, current_number_of_nodes, complexity_threshold, nodes, i, &reduced_complexity_situation);
                        }
                    }
                    // Reschedule if I have to
                    if (number_of_data_to_replicate_after_loss != 0) {
                        //~ printf("Need to re scheudle %d task\n", number_of_data_to_replicate_after_loss);
                        for (k = 0; k < number_of_data_to_replicate_after_loss; k++) {
                            data_to_store = data_to_replicate[k];
                            data_to_store_id = count + total_number_of_data_to_replicate_after_loss - number_of_data_to_replicate_after_loss + k;
                            find_closest(data_to_store, &nearest_size, &closest_index);
                            if (algorithm == 0) {
                                random_schedule(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                            }
                            else if (algorithm == 1) {
                                min_storage(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                            }
                            else if (algorithm == 10) {
                                least_used_node(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                            }
                            else if (algorithm == 9) {
                                optimal_schedule(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, combinations, total_combinations, &best_upload_time_to_print, &best_read_time_to_print, &size_stored);
                            }
                            else if (algorithm == 3) {
                                hdfs_3_replications(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                            }
                            else if (algorithm == 6) {
                                hdfs_rs(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, RS1, RS2, &total_read_time_parrallelized, &total_read_time, max_N, &size_stored);
                            }
                            else if (algorithm == 7) {
                                glusterfs(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, RS1, RS2, &total_read_time_parrallelized, &total_read_time, is_daos, max_N, &size_stored);
                            }
                            else if (algorithm == 8) {
                                glusterfs(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, RS1, RS2, &total_read_time_parrallelized, &total_read_time, is_daos, max_N, &size_stored);
                            }
                            else if (algorithm == 2) {
                                algorithm2(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, combinations, total_combinations, total_storage_size, closest_index, records_array, models, models_reconstruct, nearest_size, &list, i, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                            }
                            else if (algorithm == 4) {
                                algorithm4(current_number_of_nodes, nodes, reliability_threshold, data_to_store, max_node_size, min_data_size, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, combinations, total_combinations, &total_remaining_size, total_storage_size, closest_index, records_array, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, decision_value_alg4, &size_stored);
                            }
                            else if (algorithm == 5) {
                                balance_penalty_algorithm(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, &total_remaining_size, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                            }
                            else {
                                printf("Algorithm %d not valid\n", algorithm);
                            }
                            if (N > max_N) { printf("error N > max_N\n"); exit(1); }
                            number_of_data_stored -= 1;
                            size_stored -= data_to_store;
                            input_data_sum_of_size_already_stored += data_to_store;
                        }
                        free(data_to_replicate);
                        number_of_data_to_replicate_after_loss = 0;
                    }
                }
            }
            else {
                printf("ERROR: remove_node_pattern = %d not supported\n", remove_node_pattern);
                exit(1);
            }
            
            //~ if ((algorithm == 4 || algorithm == 2) && removed_node_index != -1) {
                //~ free_combinations(combinations, total_combinations);
                //~ combinations = reset_combinations_and_recreate_them(&total_combinations, min_number_node_in_combination, current_number_of_nodes, complexity_threshold, nodes, i, &reduced_complexity_situation);
            //~ }
        }
        
        /** Resorting the nodes and combinations after every 10 GB of data stored **/
        // TODO: sort more often ?
        if (input_data_sum_of_size_already_stored > 10000 && reduced_complexity_situation == true && algorithm == 4) {
            //~ printf("Reset\n");
            free_combinations(combinations, total_combinations);
            combinations = reset_combinations_and_recreate_them(&total_combinations, min_number_node_in_combination, current_number_of_nodes, complexity_threshold, nodes, i, &reduced_complexity_situation);
        }
        
        // First reschedule if I have to
        if (remove_node_pattern == 1 && number_of_data_to_replicate_after_loss != 0) {
            //~ printf("number_of_data_to_replicate_after_loss for replicate 1 = %d\n", number_of_data_to_replicate_after_loss);
            for (j = 0; j < number_of_data_to_replicate_after_loss; j++) {
                data_to_store = data_to_replicate[j];
                data_to_store_id = count + total_number_of_data_to_replicate_after_loss - number_of_data_to_replicate_after_loss + j;
                
                // paste all code from find to print chunks
                find_closest(data_to_store, &nearest_size, &closest_index);
                
                if (algorithm == 0) {
                    random_schedule(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                }
                else if (algorithm == 1) {
                    min_storage(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                }
                else if (algorithm == 10) {
                    least_used_node(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                }
                else if (algorithm == 9) {
                    optimal_schedule(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, combinations, total_combinations, &best_upload_time_to_print, &best_read_time_to_print, &size_stored);
                }
                else if (algorithm == 3) {
                    hdfs_3_replications(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                }
                else if (algorithm == 6) {
                    hdfs_rs(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, RS1, RS2, &total_read_time_parrallelized, &total_read_time, max_N, &size_stored);
                }
                else if (algorithm == 7) {
                    glusterfs(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, RS1, RS2, &total_read_time_parrallelized, &total_read_time, is_daos, max_N, &size_stored);
                }
                else if (algorithm == 8) {
                    glusterfs(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, RS1, RS2, &total_read_time_parrallelized, &total_read_time, is_daos, max_N, &size_stored);
                }
                else if (algorithm == 2) {
                    algorithm2(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, combinations, total_combinations, total_storage_size, closest_index, records_array, models, models_reconstruct, nearest_size, &list, i, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                }
                else if (algorithm == 4) {
                    algorithm4(current_number_of_nodes, nodes, reliability_threshold, data_to_store, max_node_size, min_data_size, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, combinations, total_combinations, &total_remaining_size, total_storage_size, closest_index, records_array, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, decision_value_alg4, &size_stored);
                }
                else if (algorithm == 5) {
                    balance_penalty_algorithm(current_number_of_nodes, nodes, reliability_threshold, data_to_store, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, &total_remaining_size, closest_index, models, models_reconstruct, nearest_size, &list, data_to_store_id, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
                }
                else {
                    printf("Algorithm %d not valid\n", algorithm);
                }
                if (N > max_N) { printf("error N > max_N\n"); exit(1); }
                
                        number_of_data_stored -= 1;
                        size_stored -= data_to_store;

                print_all_chunks(nodes, current_number_of_nodes);
                input_data_sum_of_size_already_stored += data_to_store;
            }
            free(data_to_replicate); // TODO yeah do that ? Or set it to null ?
            number_of_data_to_replicate_after_loss = 0;
        }
        
        // Then schedule the desired data I was suppose to do
        find_closest(sizes[i], &nearest_size, &closest_index);
        if (algorithm == 0) {
            random_schedule(current_number_of_nodes, nodes, current_target_reliability, sizes[i], &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, i, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
        }
        else if (algorithm == 1) {
            min_storage(current_number_of_nodes, nodes, current_target_reliability, sizes[i], &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, i, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
        }
        else if (algorithm == 10) {
            least_used_node(current_number_of_nodes, nodes, current_target_reliability, sizes[i], &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, i, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
        }
        else if (algorithm == 9) {
            optimal_schedule(current_number_of_nodes, nodes, current_target_reliability, sizes[i], &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, i, max_N, &total_read_time_parrallelized, &total_read_time, combinations, total_combinations, &best_upload_time_to_print, &best_read_time_to_print, &size_stored);
        }
        else if (algorithm == 3) {
            hdfs_3_replications(current_number_of_nodes, nodes, current_target_reliability, sizes[i], &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, i, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
        }
        else if (algorithm == 6) {
            hdfs_rs(current_number_of_nodes, nodes, current_target_reliability, sizes[i], &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, i, RS1, RS2, &total_read_time_parrallelized, &total_read_time, max_N, &size_stored);
        }
        else if (algorithm == 7) {
            glusterfs(current_number_of_nodes, nodes, current_target_reliability, sizes[i], &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, i, RS1, RS2, &total_read_time_parrallelized, &total_read_time, is_daos, max_N, &size_stored);
        }
        else if (algorithm == 8) {
            glusterfs(current_number_of_nodes, nodes, current_target_reliability, sizes[i], &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, closest_index, models, models_reconstruct, nearest_size, &list, i, RS1, RS2, &total_read_time_parrallelized, &total_read_time, is_daos, max_N, &size_stored);
        }
        else if (algorithm == 2) {
            algorithm2(current_number_of_nodes, nodes, current_target_reliability, sizes[i], &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, combinations, total_combinations, total_storage_size, closest_index, records_array, models, models_reconstruct, nearest_size, &list, i, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
        }
        else if (algorithm == 4) {
            algorithm4(current_number_of_nodes, nodes, current_target_reliability, sizes[i], max_node_size, min_data_size, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, combinations, total_combinations, &total_remaining_size, total_storage_size, closest_index, records_array, models, models_reconstruct, nearest_size, &list, i, max_N, &total_read_time_parrallelized, &total_read_time, decision_value_alg4, &size_stored);
        }
        else if (algorithm == 5) {
            balance_penalty_algorithm(current_number_of_nodes, nodes, current_target_reliability, sizes[i], &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, &total_remaining_size, closest_index, models, models_reconstruct, nearest_size, &list, i, max_N, &total_read_time_parrallelized, &total_read_time, &size_stored);
        }
        else {
            printf("Algorithm %d not valid\n", algorithm);
        }
        
        #ifdef PRINT
        printf("Algorithm %d chose N = %d and K = %d\n", algorithm, N, K);
        #endif
        
        if (N > max_N) { printf("error N > max_N\n"); exit(1); }
        
        //~ print_all_chunks(nodes, current_number_of_nodes);
         
        input_data_sum_of_size_already_stored += sizes[i];
    }
    #ifdef PRINT
    printf("Total scheduling time was %f\n", total_scheduling_time);
    #endif

    // Writting the data per data outputs
    double total_chunking_time = 0.0;
    double total_reconstruct_time = 0.0;
    
    char file_to_print[70];
    char file_to_print_time[70];
    strcpy(file_to_print, "output");
    strcat(file_to_print, "_");
    strcat(file_to_print, alg_to_print);
    strcat(file_to_print, "_stats.csv");
    strcpy(file_to_print_time, "output");
    strcat(file_to_print_time, "_");
    strcat(file_to_print_time, alg_to_print);
    strcat(file_to_print_time, "_times.csv");
    write_linked_list_to_file(&list, file_to_print, &total_chunking_time, &total_reconstruct_time);
    write_linked_list_time_to_file(&list_time, file_to_print_time);
    
    //~ printf("number_of_data_stored = %d\n", number_of_data_stored);
    if (algorithm != 9) {
        /** Writting the general outputs **/
        FILE *file = fopen(output_filename, "a");
        if (file == NULL) {
            perror("Error opening file");
            return EXIT_FAILURE;
        }
        int id_to_print_because_nodes_are_sorted = 0;
        fprintf(file, "%s, %f, %f, %f, %f, %d, %d, %f, %f, %f, \"[", alg_to_print, total_scheduling_time, total_storage_used, total_upload_time, total_parralelized_upload_time, number_of_data_stored, total_N, total_storage_used / number_of_data_stored, total_upload_time / number_of_data_stored, (double)total_N / number_of_data_stored);
        for (i = 0; i < number_of_nodes - 1; i++) {
            fprintf(file, "%f, ", initial_node_sizes[i]);
        }
        fprintf(file, "%f]\", \"[", initial_node_sizes[i]);
        for (i = 0; i < number_of_nodes - 1; i++) {
            id_to_print_because_nodes_are_sorted = 0;
            while (nodes[id_to_print_because_nodes_are_sorted].id != i) {
                id_to_print_because_nodes_are_sorted++;
            }
            fprintf(file, "%f, ", nodes[id_to_print_because_nodes_are_sorted].storage_size);
        }
        id_to_print_because_nodes_are_sorted = 0;
        while (nodes[id_to_print_because_nodes_are_sorted].id != i) {
            id_to_print_because_nodes_are_sorted++;
        }
        fprintf(file, "%f]\"", nodes[id_to_print_because_nodes_are_sorted].storage_size);
        fprintf(file, ", %f, %f, %f, %f, %f, %f, %f, %f, %f, %f\n", total_chunking_time, total_chunking_time / number_of_data_stored, total_parralelized_upload_time / number_of_data_stored, total_read_time, total_read_time / number_of_data_stored, total_read_time_parrallelized, total_read_time_parrallelized / number_of_data_stored, total_reconstruct_time, total_reconstruct_time / number_of_data_stored, size_stored);
        fclose(file);
    }
    else {
        const char *output_filename_optimal_schedule = "output_optimal_schedule.csv";
        FILE *file = fopen(output_filename_optimal_schedule, "w");
        fprintf(file, "number_of_data_stored,total_storage_used,best_upload_time,best_read_time,size_stored\n");
        fprintf(file, "%d,%f,%f,%f,%f\n", number_of_data_stored, total_storage_used, best_upload_time_to_print, best_read_time_to_print, size_stored);
        fclose(file);
    }
    printf("La\n"); fflush(stdout);
    // Free allocated memory
    free(sizes);
    free(nodes);
    for (int i = 0; i < num_files; i++) {
        free(records_array[i].n);
        free(records_array[i].k);
        free(records_array[i].avg_time);
    }
    free(records_array);
    free(records_array_reconstruct);
    free(models);
    free(models_reconstruct);
    free(combinations);
    printf("sched time %f\n", total_scheduling_time);
    return EXIT_SUCCESS;
}
