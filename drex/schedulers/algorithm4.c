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
    printf("Iteration 1\n");
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

void algorithm4(int number_of_nodes, Node *nodes, float reliability_threshold, double size, double max_node_size, double min_data_size, double total_storage_size, int *N, int *K, double* total_storage_used, double* total_upload_time, double* total_parralelized_upload_time, int* number_of_data_stored, double* total_scheduling_time, int* total_N) {
    double total_remaining_size = total_storage_size; // Used for system saturation
    
    // Heart of the function
    clock_t start, end;
    
    start = clock();
    // TODO: remove
    *N = 4;
    *K = 2;
    
    double system_saturation = get_system_saturation(number_of_nodes, min_data_size, total_storage_size, total_remaining_size);    
    printf("System saturation = %f\n", system_saturation);
    
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
