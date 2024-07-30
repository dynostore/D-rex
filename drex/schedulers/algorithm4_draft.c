#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <float.h>
#include <stdbool.h>

#define MAX_NODES 100

// Placeholder function definitions
double exponential_function(double a, double b, double c, double d, double e);
int get_max_K_from_reliability_threshold_and_nodes_chosen(int i, double reliability_threshold, double* reliability_of_nodes_chosen);
bool* is_pareto_efficient(double** costs, int len, bool maximize);
double system_saturation(double* node_sizes, double min_data_size, double total_node_size);
void update_node_sizes(int* min_set_of_nodes_chosen, int min_K, double file_size, double* node_sizes);
double predictor(double file_size, int i, int K, double* bandwidth_of_nodes_chosen);

// Structure to hold the solution data
typedef struct {
    int i;
    int K;
    int* set_of_nodes_chosen;
    double replication_and_write_time;
    double space;
} Solution;

// Function to compare doubles for qsort
int compare_doubles(const void* a, const void* b) {
    double diff = *(double*)a - *(double*)b;
    return (diff > 0) - (diff < 0);
}

/** Initialize structures **/
void init()
{
    
}

void algorithm4(
    int number_of_nodes, 
    double* reliability_of_nodes, 
    double* bandwidths, 
    double reliability_threshold, 
    double file_size, 
    double real_records, 
    double* node_sizes, 
    double max_node_size, 
    double min_data_size, 
    double (*system_saturation)(double*, double, double), 
    double total_node_size,
    double (*predictor)(double, int, int, double*),
    int* min_set_of_nodes_chosen_result, 
    int* min_N_result, 
    int* min_K_result, 
    double* node_sizes_result) {

    clock_t start = clock();

    int min_K = 0;
    int* set_of_nodes_chosen = malloc(number_of_nodes * sizeof(int));
    int* set_of_nodes = malloc(number_of_nodes * sizeof(int));
    for (int i = 0; i < number_of_nodes; i++) set_of_nodes[i] = i;

    Solution* set_of_possible_solutions = malloc(MAX_NODES * sizeof(Solution));
    double** time_space_and_size_score_from_set_of_possible_solution = malloc(MAX_NODES * sizeof(double*));
    for (int i = 0; i < MAX_NODES; i++) {
        time_space_and_size_score_from_set_of_possible_solution[i] = malloc(3 * sizeof(double));
    }

    int solutions_count = 0;
    double system_saturation_value = system_saturation(node_sizes, min_data_size, total_node_size);

    for (int i = 2; i <= number_of_nodes; i++) {
        for (int combination = 0; combination < (1 << number_of_nodes); combination++) {
            int count = 0;
            for (int j = 0; j < number_of_nodes; j++) {
                if (combination & (1 << j)) {
                    set_of_nodes_chosen[count++] = j;
                }
            }
            if (count != i) continue;

            double reliability_of_nodes_chosen[MAX_NODES];
            double bandwidth_of_nodes_chosen[MAX_NODES];

            for (int j = 0; j < i; j++) {
                reliability_of_nodes_chosen[j] = reliability_of_nodes[set_of_nodes_chosen[j]];
                bandwidth_of_nodes_chosen[j] = bandwidths[set_of_nodes_chosen[j]];
            }

            int K = get_max_K_from_reliability_threshold_and_nodes_chosen(i, reliability_threshold, reliability_of_nodes_chosen);
            if (K != -1) {
                double size_score = 0;
                bool set_of_node_valid = true;
                for (int j = 0; j < i; j++) {
                    if (node_sizes[set_of_nodes_chosen[j]] - (file_size / K) <= 0) {
                        set_of_node_valid = false;
                        break;
                    }
                    size_score += 1 - exponential_function(node_sizes[set_of_nodes_chosen[j]] - (file_size / K), max_node_size, 1, min_data_size, 1.0 / number_of_nodes);
                }

                if (set_of_node_valid) {
                    size_score /= i;
                    double replication_and_write_time = predictor(file_size, i, K, bandwidth_of_nodes_chosen);

                    set_of_possible_solutions[solutions_count] = (Solution) {
                        .i = i, .K = K, .set_of_nodes_chosen = malloc(i * sizeof(int)),
                        .replication_and_write_time = replication_and_write_time, .space = (file_size / K) * i
                    };
                    for (int j = 0; j < i; j++) {
                        set_of_possible_solutions[solutions_count].set_of_nodes_chosen[j] = set_of_nodes_chosen[j];
                    }

                    time_space_and_size_score_from_set_of_possible_solution[solutions_count][0] = replication_and_write_time;
                    time_space_and_size_score_from_set_of_possible_solution[solutions_count][1] = (file_size / K) * i;
                    time_space_and_size_score_from_set_of_possible_solution[solutions_count][2] = size_score;

                    solutions_count++;
                }
            }
        }
    }

    if (solutions_count == 0) {
        printf("Algorithm 4 could not find a solution that would not overflow the memory of the nodes\n");
        return;
    }

    bool* set_of_solution_on_pareto = is_pareto_efficient(time_space_and_size_score_from_set_of_possible_solution, solutions_count, false);

    double time_on_pareto[MAX_NODES];
    double space_score_on_pareto[MAX_NODES];
    int pareto_count = 0;

    for (int i = 0; i < solutions_count; i++) {
        if (set_of_solution_on_pareto[i]) {
            time_on_pareto[pareto_count] = time_space_and_size_score_from_set_of_possible_solution[i][0];
            space_score_on_pareto[pareto_count] = time_space_and_size_score_from_set_of_possible_solution[i][2];
            pareto_count++;
        }
    }

    qsort(time_on_pareto, pareto_count, sizeof(double), compare_doubles);
    qsort(space_score_on_pareto, pareto_count, sizeof(double), compare_doubles);

    double min_time = time_on_pareto[0];
    double max_time = time_on_pareto[pareto_count - 1];
    double min_space_score = space_score_on_pareto[0];
    double max_space_score = space_score_on_pareto[pareto_count - 1];

    double total_progress_time = max_time - min_time;
    double total_progress_space = time_space_and_size_score_from_set_of_possible_solution[set_of_solution_on_pareto[pareto_count - 1]][1] - time_space_and_size_score_from_set_of_possible_solution[set_of_solution_on_pareto[0]][1];
    double total_progress_space_score = max_space_score - min_space_score;

    double max_score = -1;
    int best_index = -1;

    for (int i = 0; i < pareto_count; i++) {
        double both_space_score = 0;
        double time_score = 0;

        if (total_progress_time > 0) {
            time_score = 100 - ((time_on_pareto[i] - min_time) * 100) / total_progress_time;
        }

        if (total_progress_space > 0) {
            both_space_score += 100 - ((time_space_and_size_score_from_set_of_possible_solution[set_of_solution_on_pareto[i]][1] - time_space_and_size_score_from_set_of_possible_solution[set_of_solution_on_pareto[pareto_count - 1]][1]) * 100) / total_progress_space;
        }

        if (total_progress_space_score > 0) {
            both_space_score += 100 - ((space_score_on_pareto[i] - min_space_score) * 100) / total_progress_space_score;
        }

        double total_score = time_score + (both_space_score / 2) * system_saturation_value;

        if (max_score < total_score) {
            max_score = total_score;
            best_index = i;
        }
    }

    *min_N_result = set_of_possible_solutions[set_of_solution_on_pareto[best_index]].i;
    *min_K_result = set_of_possible_solutions[set_of_solution_on_pareto[best_index]].K;
    int chosen_node_count = set_of_possible_solutions[set_of_solution_on_pareto[best_index]].i;
    for (int i = 0; i < chosen_node_count; i++) {
        min_set_of_nodes_chosen_result[i] = set_of_possible_solutions[set_of_solution_on_pareto[best_index]].set_of_nodes_chosen[i];
    }

    update_node_sizes(min_set_of_nodes_chosen_result, *min_K_result, file_size, node_sizes);

    for (int i = 0; i < number_of_nodes; i++) {
        node_sizes_result[i] = node_sizes[i];
    }

    clock_t end = clock();
    double time_taken = ((double)(end - start)) / CLOCKS_PER_SEC;
    printf("\nAlgorithm 4 chose N = %d and K = %d with the set of nodes: [", *min_N_result, *min_K_result);
    for (int i = 0; i < chosen_node_count; i++) {
        printf("%d ", min_set_of_nodes_chosen_result[i]);
    }
    printf("]. It took %f seconds.\n", time_taken);

    // Free allocated memory
    free(set_of_nodes_chosen);
    free(set_of_nodes);
    for (int i = 0; i < MAX_NODES; i++) {
        free(time_space_and_size_score_from_set_of_possible_solution[i]);
    }
    free(time_space_and_size_score_from_set_of_possible_solution);
    free(set_of_possible_solutions);
}

// Implement placeholder functions here

double exponential_function(double a, double b, double c, double d, double e) {
    // Placeholder implementation
    return exp(a);
}

int get_max_K_from_reliability_threshold_and_nodes_chosen(int i, double reliability_threshold, double* reliability_of_nodes_chosen) {
    // Placeholder implementation
    return i;
}

bool* is_pareto_efficient(double** costs, int len, bool maximize) {
    // Placeholder implementation
    bool* result = malloc(len * sizeof(bool));
    for (int i = 0; i < len; i++) result[i] = true;
    return result;
}

double system_saturation(double* node_sizes, double min_data_size, double total_node_size) {
    // Placeholder implementation
    return 1.0;
}

void update_node_sizes(int* min_set_of_nodes_chosen, int min_K, double file_size, double* node_sizes) {
    // Placeholder implementation
}

double predictor(double file_size, int i, int K, double* bandwidth_of_nodes_chosen) {
    // Placeholder implementation
    return file_size / K;
}

int main() {
    // Example usage
    int number_of_nodes = 4;
    double reliability_of_nodes[] = {0.9, 0.8, 0.95, 0.85};
    double bandwidths[] = {10.0, 20.0, 30.0, 40.0};
    double reliability_threshold = 0.8;
    double file_size = 100.0;
    double real_records = 10.0;
    double node_sizes[] = {50.0, 60.0, 70.0, 80.0};
    double max_node_size = 100.0;
    double min_data_size = 5.0;
    double total_node_size = 200.0;

    int min_set_of_nodes_chosen_result[MAX_NODES];
    int min_N_result;
    int min_K_result;
    double node_sizes_result[MAX_NODES];

    algorithm4(
        number_of_nodes, 
        reliability_of_nodes, 
        bandwidths, 
        reliability_threshold, 
        file_size, 
        real_records, 
        node_sizes, 
        max_node_size, 
        min_data_size, 
        system_saturation, 
        total_node_size, 
        predictor,
        min_set_of_nodes_chosen_result, 
        &min_N_result, 
        &min_K_result, 
        node_sizes_result
    );

    return 0;
}
