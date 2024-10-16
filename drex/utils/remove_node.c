#include <stdio.h>
#include <float.h>
#include <stdlib.h>
#include <../schedulers/algorithm4.h>
#include <remove_node.h>
#include <time.h>

double* reschedule_lost_chunks(Node* removed_node, Node* nodes, int number_of_nodes, int* number_of_data_to_replicate_after_loss, int alg) {
    int i = 0;
    int j = 0;
    int k = 0;
    int number_of_lost_chunks = 0;
    Chunk* current_chunk = NULL;
    //~ printf("Start of reschedule_lost_chunks\n"); fflush(stdout);
    if (removed_node->chunks->head != NULL) {
        current_chunk = removed_node->chunks->head;
        while (current_chunk != NULL) {
            number_of_lost_chunks++;
            current_chunk = current_chunk->next;
        }
    }
    
    //~ printf("number_of_lost_chunks = %d\n", number_of_lost_chunks);
    *number_of_data_to_replicate_after_loss += number_of_lost_chunks;

    if (number_of_lost_chunks != 0) {
        current_chunk = removed_node->chunks->head;
        double* chunk_sizes = malloc(number_of_lost_chunks*sizeof(double));
        double* data_to_replicate = malloc(number_of_lost_chunks*sizeof(double));
        int* chunk_ids = malloc(number_of_lost_chunks*sizeof(int));
        int** chunk_nodes_used = malloc(number_of_lost_chunks*sizeof(int*));
        int* num_of_nodes_used = malloc(number_of_lost_chunks*sizeof(int));
                        
        for (i = 0; i < number_of_lost_chunks; i++) {
            chunk_sizes[i] = current_chunk->chunk_size;

            chunk_ids[i] = current_chunk->chunk_id;

            data_to_replicate[i] = current_chunk->original_data_size;

            chunk_nodes_used[i] = malloc(current_chunk->num_of_nodes_used * sizeof(int));

            num_of_nodes_used[i] = current_chunk->num_of_nodes_used;

            for (j = 0; j < current_chunk->num_of_nodes_used; j++) {
                chunk_nodes_used[i][j] = current_chunk->nodes_used[j];
            }
            current_chunk = current_chunk->next;
        }
                
        for (i = 0; i < number_of_lost_chunks; i++) {                
            // Add space
            //~ if (i%10000 == 0) {            printf("i = %d/%d chunk_sizes[i] %f num_of_nodes_used[i] %d number_of_nodes %d\n", i, number_of_lost_chunks, chunk_sizes[i], num_of_nodes_used[i], number_of_nodes); }
            //~ printf("total_remaining_size before = %f\n", *total_remaining_size);
            for (j = 0; j < num_of_nodes_used[i]; j++) {
                for (k = 0; k < number_of_nodes; k++) {
                    if (nodes[k].id == chunk_nodes_used[i][j]) {
                        nodes[k].storage_size += chunk_sizes[i];
                    }
                }
            }
            remove_chunk_from_node(chunk_nodes_used[i], num_of_nodes_used[i], chunk_ids[i], nodes, number_of_nodes);
        }
        
        if (alg != 3) {
            free(chunk_ids);
            free(num_of_nodes_used);
            for (i = 0; i < number_of_lost_chunks; i++) {
                if (chunk_nodes_used[i] != NULL) {
                    free(chunk_nodes_used[i]);
                }
            }
            free(chunk_sizes);
            free(chunk_nodes_used);
        }
        
        return data_to_replicate;
    }
    else {
        //~ printf("End of reschedule_lost_chunks 2\n"); fflush(stdout);
        //~ *data_to_replicate = NULL;
        return NULL;
    }
}

int check_if_node_failed(Node *node) {
    // Generate a random number between 0 and 1
    double random_value = (double)rand() / RAND_MAX;
        
    // Check if the random value indicates a failure
    if (random_value <= node->daily_failure_rate) {
        //~ printf("random_value %f <= node->daily_failure_rate %f\n", random_value, node->daily_failure_rate); 
        return 1;  // Node failed
    } else {
        return 0;  // Node did not fail
    }
}

int remove_random_node (int number_of_nodes, Node* node, int* removed_node_id) {
    int random_number = rand() % (number_of_nodes);
    //~ printf("Randomly chose node at index %d to fail\n", random_number);
    node[random_number].add_after_x_jobs = -1;
    *removed_node_id = node[random_number].id;
    return random_number;
}

int remove_node_following_failure_rate (int number_of_nodes, Node* nodes, int* removed_node_id, int time) {
    for (int i = 0; i < number_of_nodes; i++) {
        if (check_if_node_failed(&nodes[i])) {
            //~ printf("Node %d failed at time %d\n", nodes[i].id, time);
            nodes[i].add_after_x_jobs = -1;
            *removed_node_id = nodes[i].id;
            return i;
        }
    }
    return -1;
}
