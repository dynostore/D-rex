#include <stdio.h>
#include <float.h>
#include <stdlib.h>
#include <../schedulers/algorithm4.h>
#include <remove_node.h>
#include <time.h>

void reschedule_lost_chunks(Node* removed_node, Node* nodes, int number_of_nodes, double* total_remaining_size) {
    printf("Start of reschedule_lost_chunks for node %d\n", removed_node->id);
    int i = 0;
    int j = 0;
    if (removed_node->chunks->head != NULL) {
        Chunk* current_chunk = removed_node->chunks->head;
        while (current_chunk != NULL) {
            printf("Remove chunk %d from:\n", current_chunk->chunk_id);
            for (i = 0; i < current_chunk->num_of_nodes_used; i++) {
                printf("%d ", current_chunk->nodes_used[i]);
            }
            printf("\n");
            
            // Find node to remove from
            for (i = 0; i < current_chunk->num_of_nodes_used; i++) {
                for (j = 0; j < number_of_nodes; j++) {
                    if (nodes[j].id == current_chunk->nodes_used[i]) {
                        // Remove space
                        nodes[j].storage_size += current_chunk->chunk_size;
                        *total_remaining_size += current_chunk->chunk_size;
                        printf("Adding %f to node %d\n", current_chunk->chunk_size, nodes[j].id);
                    }
                }
            }
            
            printf("total_remaining_size = %f\n", *total_remaining_size);
            
            // Remove chunks
            remove_shared_chunk_from_nodes(current_chunk->nodes_used, current_chunk->num_of_nodes_used, current_chunk->chunk_id, nodes, number_of_nodes);
                    
            print_all_chunks(nodes, number_of_nodes);
            exit(1);        
            
            // Remove actually all chunks of these data and update all storage, even on nodes that did not lost the chunks because you'll need to recreate the cunks from scratch. So need to remove from all nodes all chunks lost and reschedule from 0 this data
                        
            current_chunk = current_chunk->next;
        }
        
        // Call the algorithms again
        //~ current_chunk = removed_node->chunks->head;
        //~ while (current_chunk != NULL) {
            
            
            // Add the added chunks again
            
            
            //~ current_chunk = current_chunk->next;
        //~ }
    }
}

int check_if_node_failed(Node *node) {
    // Generate a random number between 0 and 1
    double random_value = (double)rand() / RAND_MAX;
    
    //~ printf("random_value in check if node failed %f daily failure rate of current node is %f\n", random_value, node->daily_failure_rate);
    
    // Check if the random value indicates a failure
    if (random_value <= node->daily_failure_rate) {
        return 1;  // Node failed
    } else {
        return 0;  // Node did not fail
    }
}

int remove_random_node (int number_of_nodes, Node* node, int* removed_node_id) {
    int random_number = rand() % (number_of_nodes);
    printf("Randomly chose node at index %d to fail\n", random_number);
    node[random_number].add_after_x_jobs = -1;
    *removed_node_id = node[random_number].id;
    return random_number;
}

int remove_node_following_failure_rate (int number_of_nodes, Node* nodes, int* removed_node_id) {
    for (int i = 0; i < number_of_nodes; i++) {
        if (check_if_node_failed(&nodes[i])) {
            printf("Node %d failed\n", nodes[i].id);
            nodes[i].add_after_x_jobs = -1;
            *removed_node_id = nodes[i].id;
            return i;
        }
    }
    return -1;
}
