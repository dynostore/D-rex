#include <stdio.h>
#include <stdlib.h>

// Global variable for the number of nodes
int number_of_nodes = 0;

typedef struct {
    int id;
    long storage_size;
    int write_bandwidth;
    int read_bandwidth;
    float annual_failure_rate;
} Node;

// Function to count the number of nodes in the file
void count_nodes(const char *filename) {
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
    number_of_nodes = count - 1;  // Adjust if there is no header
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

// Function to read data from file and populate the nodes array
void read_node(const char *filename, Node *nodes) {
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
    while (fscanf(file, "%d,%ld,%d,%d,%f",
                  &nodes[index].id,
                  &nodes[index].storage_size,
                  &nodes[index].write_bandwidth,
                  &nodes[index].read_bandwidth,
                  &nodes[index].annual_failure_rate) == 5) {
        index++;
    }

    fclose(file);
}

// Function to read data from file and populate the sizes array
void read_data(const char *filename, float *sizes, int *size_count) {
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
    *size_count = 0;

    while (fgets(line, sizeof(line), file)) {
        // Parse the line
        if (sscanf(line, "%*d,%f,%*f,%*f,%d", &temp_size, &temp_access_type) == 2) {
            if (temp_access_type == 2) {
                sizes[*size_count] = temp_size;
                (*size_count)++;
            }
        } else {
            fprintf(stderr, "Error parsing line: %s\n", line);
        }
    }

    fclose(file);
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <input_node> <input_data>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *input_node = argv[1];
    const char *input_data = argv[2];

    // Step 1: Count the number of lines with Access Type 2
    int count = count_lines_with_access_type(input_data);
    count_nodes(input_node);

    // Step 2: Allocate memory for the sizes array
    float *sizes = (float *)malloc(count * sizeof(float));
    if (sizes == NULL) {
        perror("Error allocating memory");
        return EXIT_FAILURE;
    }
    Node *nodes = (Node *)malloc(number_of_nodes * sizeof(Node));
    if (nodes == NULL) {
        perror("Error allocating memory");
        return EXIT_FAILURE;
    }

    // Step 3: Read data into the sizes array
    int size_count;
    read_data(input_data, sizes, &size_count);
    read_node(input_node, nodes);

    // Print the collected sizes
    printf("Sizes with Access Type 2:\n");
    for (int i = 0; i < size_count; i++) {
        printf("%.2f\n", sizes[i]);
    }
    for (int i = 0; i < number_of_nodes; i++) {
        printf("Node %d: storage_size=%ld, write_bandwidth=%d, read_bandwidth=%d, annual_failure_rate=%.2f\n",
               nodes[i].id, nodes[i].storage_size, nodes[i].write_bandwidth,
               nodes[i].read_bandwidth, nodes[i].annual_failure_rate);
    }

    set_of_nodes_chosen, N, K, node_sizes = algorithm4(number_of_nodes, reliability_nodes,write_bandwidths, reliability_threshold, data, real_records, node_sizes, max_node_size,min_data_size, system_saturation, total_storage_size, predictor)

    // Free allocated memory
    free(sizes);
    free(nodes);

    return EXIT_SUCCESS;
}

