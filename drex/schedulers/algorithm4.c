#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <limits.h>
#include <math.h>
#include <time.h>

typedef struct {
    int id;
    double storage_size;
    int write_bandwidth;
    int read_bandwidth;
    double probability_failure;
} Node;


typedef struct {
    int num_elements;
    Node **nodes; // Array of pointers to Node structs
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
double probability_of_failure(double failure_rate, int data_duration_on_system) {
    // Convert data duration to years
    double data_duration_in_years = data_duration_on_system / 365.0;
    
    // Convert failure rate to a fraction
    double lambda_rate = failure_rate / 100.0;
    
    // Calculate the probability of failure
    double probability_failure = 1 - exp(-lambda_rate * data_duration_in_years);
    
    return probability_failure;
}

// Function to read data from file and populate the nodes array
void read_node(const char *filename, int number_of_nodes, Node *nodes, int data_duration_on_system, double* max_node_size, double* total_storage_size, double* initial_node_sizes) {
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

// Function to recursively generate combinations
void generate_combinations_recursive(Node *nodes, int num_nodes, Combination **combinations, int *comb_index, int start, int end, int index, int r) {
    if (index == r) {
        for (int i = 0; i < r; i++) {
            combinations[*comb_index]->nodes[i] = &nodes[i];
        }
        (*comb_index)++;
        return;
    }

    for (int i = start; i <= end && end - i + 1 >= r - index; i++) {
        combinations[*comb_index]->nodes[index] = &nodes[i];
        generate_combinations_recursive(nodes, num_nodes, combinations, comb_index, i + 1, end, index + 1, r);
    }
}

// Function to generate combinations
void generate_combinations(Node *nodes, int num_nodes, int min_size, int max_size) {
    int i, j, k;
    int total_combinations = 0;
    Combination **combinations = NULL;

    // Calculate the total number of combinations
    for (i = min_size; i <= max_size; i++) {
        total_combinations += combination(num_nodes, i);
    }

    // Allocate memory for storing all combinations
    combinations = malloc(total_combinations * sizeof(Combination *));
    if (combinations == NULL) {
        perror("Error allocating memory for combinations");
        exit(EXIT_FAILURE);
    }

    int comb_index = 0;
    for (i = min_size; i <= max_size; i++) {
        int num_combinations = combination(num_nodes, i);
        Combination **temp_combinations = malloc(num_combinations * sizeof(Combination *));
        if (temp_combinations == NULL) {
            perror("Error allocating memory for temporary combinations");
            exit(EXIT_FAILURE);
        }

        for (j = 0; j < num_combinations; j++) {
            temp_combinations[j] = malloc(sizeof(Combination));
            if (temp_combinations[j] == NULL) {
                perror("Error allocating memory for combination");
                exit(EXIT_FAILURE);
            }
            temp_combinations[j]->nodes = malloc(i * sizeof(Node *));
            if (temp_combinations[j]->nodes == NULL) {
                perror("Error allocating memory for nodes in combination");
                exit(EXIT_FAILURE);
            }
            temp_combinations[j]->num_elements = i;
        }

        // Generate combinations and store them
        int index = 0;
        generate_combinations_recursive(nodes, num_nodes, temp_combinations, &index, 0, num_nodes - 1, 0, i);

        // Copy temporary combinations to the main array
        for (j = 0; j < num_combinations; j++) {
            combinations[comb_index++] = temp_combinations[j];
        }
        free(temp_combinations);
    }

    // Print all combinations
    for (i = 0; i < total_combinations; i++) {
        printf("Combination %d:\n", i + 1);
        print_combination(combinations[i]);
        printf("\n");
    }

    // Free allocated memory
    free_combinations(combinations, total_combinations);
}

void algorithm4(int number_of_nodes, Node *nodes, float reliability_threshold, double size, double max_node_size, double min_data_size, double total_storage_size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N) {
    double total_remaining_size = total_storage_size; // Used for system saturation
    int i = 0;
    
    // Heart of the function
    clock_t start, end;
    
    start = clock();
    // TODO: remove
    *N = 4;
    *K = 2;

    // 1. Get system saturation
    double system_saturation = get_system_saturation(number_of_nodes, min_data_size, total_storage_size, total_remaining_size);    
    printf("System saturation = %f\n", system_saturation);
    
    // 2. Iterates over a range of nodes combination
    
    exit(1);
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
    }
    *total_scheduling_time += ((double) (end - start)) / CLOCKS_PER_SEC;
}

int main(int argc, char *argv[]) {
    int i = 0;
    int j = 0;
    if (argc < 6) {
        fprintf(stderr, "Usage: %s <input_node> <input_data> <data_duration_on_system> <reliability_threshold> <number_of_repetition>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *input_node = argv[1];
    const char *input_data = argv[2];
    int data_duration_on_system = atoi(argv[3]);
    double reliability_threshold = atof(argv[4]);
    int number_of_repetition = atoi(argv[5]);
    printf("Data have to stay %d days on the system. Reliability threshold is %f. Number of repetition is %d\n", data_duration_on_system, reliability_threshold, number_of_repetition);
    
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
    int max_number_node_in_combination = 2;
    for (i = min_number_node_in_combination; i <= max_number_node_in_combination; i++) {
        total_combinations += combination(number_of_nodes, i);
    }
    printf("There are %d possible combinations\n", total_combinations);
    
    // Generate all possibles combinations
    generate_combinations(nodes, number_of_nodes, min_number_node_in_combination, max_number_node_in_combination);
    exit(1);
    
    // Looping on all data
    for (i = 0; i < count; i++) {
        if (min_data_size > sizes[i]) {
            min_data_size = sizes[i];
        }
        algorithm4(number_of_nodes, nodes, reliability_threshold, sizes[i], max_node_size, min_data_size, total_storage_size, &N, &K, &total_storage_used, &total_upload_time, &total_parralelized_upload_time, &number_of_data_stored, &total_scheduling_time, &total_N);
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

    return EXIT_SUCCESS;
}
