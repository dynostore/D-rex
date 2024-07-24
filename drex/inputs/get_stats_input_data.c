#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUFFER_SIZE 1024

void calculate_sum(const char *file_path) {
    FILE *file = fopen(file_path, "r");
    if (file == NULL) {
        fprintf(stderr, "Could not open file %s for reading\n", file_path);
        exit(EXIT_FAILURE);
    }

    char buffer[BUFFER_SIZE];
    double sum_read = 0.0;
    double sum_write = 0.0;

    // Read and ignore the header line
    if (fgets(buffer, BUFFER_SIZE, file) == NULL) {
        fprintf(stderr, "Could not read header from file %s\n", file_path);
        fclose(file);
        exit(EXIT_FAILURE);
    }

    // Read each line of the file
    while (fgets(buffer, BUFFER_SIZE, file)) {
        char *token;
        int access_type;
        double size;

        // Skip the first token (Unique ID)
        token = strtok(buffer, ",");
        if (token == NULL) continue;

        // Get the size
        token = strtok(NULL, ",");
        if (token == NULL) continue;
        size = atof(token);

        // Skip the next two tokens (Relative Time, Time Spent)
        token = strtok(NULL, ",");
        if (token == NULL) continue;
        token = strtok(NULL, ",");
        if (token == NULL) continue;

        // Get the access type
        token = strtok(NULL, ",");
        if (token == NULL) continue;
        access_type = atoi(token);

        // Update the corresponding sum
        if (access_type == 1) {
            sum_read += size;
        } else if (access_type == 2) {
            sum_write += size;
        }
    }

    fclose(file);

    printf("The sum of the 'size' column for Access Type 1 (read) is: %.2f\n", sum_read);
    printf("The sum of the 'size' column for Access Type 2 (write) is: %.2f\n", sum_write);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <file_path>\n", argv[0]);
        return EXIT_FAILURE;
    }

    calculate_sum(argv[1]);

    return EXIT_SUCCESS;
}

