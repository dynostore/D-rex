#include <stdio.h>
#include <float.h>
#include <stdlib.h>
#include <../schedulers/algorithm4.h>
#include <remove_node.h>
#include <time.h>

void reschedule_lost_chunks(Node* removed_node) {
    //~ printf("Start of reschedule_lost_chunks for node %d\n", removed_node->id);
    //~ int i = 0;
    //~ int j = 0;
    //~ if (removed_node->chunks->head != NULL) {
        //~ Chunk* current_chunk = removed_node->chunks->head;
        //~ while (current_chunk != NULL) {
            //~ printf("Chunk ID: %d / Size: %f / ", current_chunk->chunk_id, current_chunk->chunk_size);
            //~ printf("Number of Nodes Used: %d / ", current_chunk->num_of_nodes_used);
            //~ printf("Nodes Holding This Chunk: ");
            //~ printf("Remove chunk %d\n", current_chunk->chunk_id);
            //~ for (i = 0; i < current_chunk->num_of_nodes_used; i++) {
                //~ printf("%d ", current_chunk->nodes_used[i]);
            //~ }
            //~ printf("\n");

            // Find node to remove from
            //~ for (j = 0; j <  current_chunk->nodes_used[i]
            
            //~ // Remove space
            //~ for (i = 0; i < current_chunk->num_of_nodes_used; i++) {
                //~ current_chunk->nodes_used[i]->storage_size += current_chunk->chunk_size;
                //~ printf("Adding %f to node %d\n", current_chunk->chunk_size, current_chunk->nodes_used[i]->id);
            //~ }
            
            // Remove chunks
            //~ printf("Remove chunk %d\n", current_chunk->chunk_id);
            //~ remove_shared_chunk_from_nodes(current_chunk->nodes_used, current_chunk->num_of_nodes_used, current_chunk->chunk_id);
            //~ return;
            // Would need to update total_storage_size and total_remaining_size if alg4 used them but it does not soo no need
                        
            //~ current_chunk = current_chunk->next;
        //~ }
        
        // Call the algorithms again
        //~ current_chunk = removed_node->chunks->head;
        //~ while (current_chunk != NULL) {
            
            
            // Add the added chunks again
            
            
            //~ current_chunk = current_chunk->next;
        //~ }
    //~ }
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

int remove_random_node (int number_of_nodes, Node* node) {
    int random_number = rand() % (number_of_nodes);
    printf("Randomly chose node at index %d to fail\n", random_number);
    node[random_number].add_after_x_jobs = -1;
    return random_number;
}

int remove_node_following_failure_rate (int number_of_nodes, Node* nodes) {
    for (int i = 0; i < number_of_nodes; i++) {
        if (check_if_node_failed(&nodes[i])) {
            printf("Node at index %d: %d failed\n", i, nodes[i].id);
            nodes[i].add_after_x_jobs = -1;
            return i;
        }
    }
    return -1;
}
