#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <limits.h>
#include <math.h>
#include <time.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    int id;
    double storage_size;
    int write_bandwidth;
    int read_bandwidth;
    double probability_failure;
} Node;

typedef struct {
    int size;
    double* n;
    double* k;
    double* avg_time;
} RealRecords;

typedef struct {
    int num_elements; // Number of nodes in the combination
    Node** nodes; // Array of pointers to Node structs
    double* probability_failure; // Array of reliability
    double variance_reliability; // To avoid having to compute it all the time
    double sum_reliability; // To avoid having to compute it all the time
    int* write_bandwidth; // Array of bandwidths
    double min_remaining_size; // Smallest node's remaining memory in the combination. Used to quickly skip an unvalid combination
    int min_write_bandwidth; // Smallest node's write bandwidth in the combination
} Combination;

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
    printf("mean %f\n", mean);
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

void algorithm4(int number_of_nodes, Node *nodes, float reliability_threshold, double size, double max_node_size, double min_data_size, double total_storage_size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N, Combination **combinations, int total_combinations) {
    double total_remaining_size = total_storage_size; // Used for system saturation
    int i = 0;
    int j = 0;
    double size_score = 0;
    double replication_and_write_time = 0;
    double chunk_size = 0;
    double one_on_number_of_nodes = 1.0/number_of_nodes;
    
    // Heart of the function
    clock_t start, end;
    
    start = clock();
    // TODO: remove
    *N = 4;
    *K = 2;

    // 1. Get system saturation
    double system_saturation = get_system_saturation(number_of_nodes, min_data_size, total_storage_size, total_remaining_size);    
    printf("System saturation = %f\n", system_saturation);
    printf("Data size = %f\n", size);
    
    // 2. Iterates over a range of nodes combination
    for (i = 0; i < total_combinations; i++) {
        *K = get_max_K_from_reliability_threshold_and_nodes_chosen(combinations[i]->num_elements, reliability_threshold, combinations[i]->sum_reliability, combinations[i]->variance_reliability);
        printf("Max K for combination %d is %d\n", i, *K);
        if (*K != -1) {
            chunk_size = size/(*K);
            printf("Chunk size: %f\n", chunk_size);
            if (combinations[i]->min_remaining_size - chunk_size >= 0) {
                size_score = 0;
                for (j = 0; j < combinations[i]->num_elements; j++) {
                    size_score += 1 - exponential_function(combinations[i]->nodes[j]->storage_size - chunk_size, max_node_size, 1, min_data_size, one_on_number_of_nodes);
                    printf("%f %f %f %f %f\n", combinations[i]->nodes[j]->storage_size, chunk_size, max_node_size, min_data_size, one_on_number_of_nodes);
                    printf("size_score: %f\n", size_score);
                }
                size_score = size_score/combinations[i]->num_elements;
                printf("size_score: %f\n", size_score);
                //~ replication_and_write_time = predict();
                printf("replication_and_write_time: %f\n", replication_and_write_time);
            }
            exit(1);
        }
    }
    
    end = clock();
        
    // Computing the results
    if (*N != -1) {
        *number_of_data_stored += 1;
        *total_N += *N;
        *total_storage_used += (size / *K) * *N;
        
        // TODO: compute these two values
        //~ total_upload_time +=
        //~ total_parralelized_upload_time += 
        
        // TODO: update total_remaining_size
        
        // TODO: update combinations[*combination_count]->min_remaining_size
    }
    *total_scheduling_time += ((double) (end - start)) / CLOCKS_PER_SEC;
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

// Function to free the memory allocated for RealRecords
void free_records(RealRecords *records) {
    free(records->n);
    free(records->k);
    free(records->avg_time);
}

int main(int argc, char *argv[]) {
    int i = 0;
    //~ int j = 0;
    //~ int k = 0;
    if (argc < 6) {
        fprintf(stderr, "Usage: %s <input_node> <input_data> <data_duration_on_system> <reliability_threshold> <number_of_repetition>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *input_node = argv[1];
    const char *input_data = argv[2];
    double data_duration_on_system = atof(argv[3]);
    double reliability_threshold = atof(argv[4]);
    int number_of_repetition = atoi(argv[5]);
    printf("Data have to stay %f days on the system. Reliability threshold is %f. Number of repetition is %d\n", data_duration_on_system, reliability_threshold, number_of_repetition);
    
    // Step 1: Count the number of lines
    int count = count_lines_with_access_type(input_data);
    count = count*number_of_repetition;
    int number_of_nodes = count_nodes(input_node);

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
    read_node(input_node, number_of_nodes, nodes, data_duration_on_system, &max_node_size, &total_storage_size, initial_node_sizes);
    
    // Print the collected data
    #ifdef PRINT
    printf("There are %d data in W mode:\n", count);
    for (i = 0; i < count; i++) {
        printf("%.2f\n", sizes[i]);
    }
    for (i = 0; i < number_of_nodes; i++) {
        printf("Node %d: storage_size=%f, write_bandwidth=%d, read_bandwidth=%d, probability_failure=%f\n",
               nodes[i].id, nodes[i].storage_size, nodes[i].write_bandwidth,
               nodes[i].read_bandwidth, nodes[i].probability_failure);
    }
    printf("Max node size is %f\n", max_node_size);
    printf("Total storage size is %f\n", total_storage_size);
    #endif
    
    // Variables used in algorithm4
    double min_data_size = DBL_MAX;
    int N;
    int K;
    const char *output_filename = "output_drex_only.csv";
    const char *alg_to_print = "alg4";
    double total_scheduling_time = 0;
    double total_storage_used = 0;
    double total_upload_time = 0;
    double total_parralelized_upload_time = 0;
    int number_of_data_stored = 0;
    int total_N = 0; // Number of chunks
    
    // Calculate total number of combinations
    int total_combinations = 0;
    int min_number_node_in_combination = 2;
    int max_number_node_in_combination = number_of_nodes;
    for (i = min_number_node_in_combination; i <= max_number_node_in_combination; i++) {
        total_combinations += combination(number_of_nodes, i);
    }
    printf("There are %d possible combinations\n", total_combinations);
    
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
        printf("combination_count = %d\n", combination_count);
        create_combinations(nodes, number_of_nodes, i, combinations, &combination_count);
    }
    
    #ifdef PRINT
    for (j = 0; j < total_combinations; j++) {
        printf("Combination %d: ", j + 1);
        for (k = 0; k < combinations[j]->num_elements; k++) {
            printf("%d ", combinations[j]->nodes[k]->id);
            printf("%d - ", combinations[j]->write_bandwidth[k]);
        }
        printf("\n");
    }
    #endif
    
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
    #ifdef PRINT
    // Print the data to verify (example for the first file)
    for (i = 0; i < 171; i++) {
        printf("File %s, Row %d: n: %.2f, k: %.2f, avg_time: %.6f\n", filenames[0], i, records_array[0].n[i], records_array[0].k[i], records_array[0].avg_time[i]);
    }
    #endif
    
    // Looping on all data and using algorithm4
    for (i = 0; i < count; i++) {
        if (min_data_size > sizes[i]) {
            min_data_size = sizes[i];
        }
        algorithm4(number_of_nodes, nodes, reliability_threshold, sizes[i], max_node_size, min_data_size, total_storage_size, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N, combinations, total_combinations);
        #ifdef PRINT
        printf("Algorithm 4 chose N = %d and K = %d\n", N, K);
        #endif
        if (i%1000 == 0) {
            printf("%d/%d\n", i, count);
        }
    }
    #ifdef PRINT
    printf("Total scheduling time was %f\n", total_scheduling_time);
    #endif
        
    // Writting the outputs
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
        
    // Free allocated memory
    free(sizes);
    free(nodes);
    for (i = 0; i < num_files; i++) {
        free_records(&records_array[i]);
    }
    free(records_array);
    
    printf("Success\n");
    return EXIT_SUCCESS;
}
