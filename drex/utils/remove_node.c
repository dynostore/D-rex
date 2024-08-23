#include <stdio.h>
#include <float.h>
#include <stdlib.h>
#include <../schedulers/algorithm4.h>
#include <remove_node.h>
#include <time.h>

void reschedule_lost_chunks(Node* removed_node) {
    printf("Start of reschedule_lost_chunks for node %d\n", removed_node->id);
    
    if (removed_node->chunks->head != NULL) {
            //~ printf("Node ID: %d\n", nodes[i].id);
            //~ Chunk* current_chunk = nodes[i].chunks->head;
            //~ while (current_chunk != NULL) {
                //~ printf("Chunk ID: %d / Size: %f / ", current_chunk->chunk_id, current_chunk->chunk_size);
                //~ printf("Number of Nodes Used: %d / ", current_chunk->num_of_nodes_used);
                //~ printf("Nodes Holding This Chunk: ");
                //~ for (int j = 0; j < current_chunk->num_of_nodes_used; j++) {
                    //~ printf("%d ", current_chunk->nodes_used[j]);
                //~ }
                //~ printf("\n");
                //~ current_chunk = current_chunk->next;
            //~ }
            //~ printf("\n");  // Separate nodes by a newline
    }
}

int check_if_node_failed(Node *node) {
    // Generate a random number between 0 and 1
    double random_value = (double)rand() / RAND_MAX;
    
    printf("random_value in check if node failed %f daily failure rate of current node is %f\n", random_value, node->daily_failure_rate);
    
    // Check if the random value indicates a failure
    if (random_value <= node->daily_failure_rate) {
        return 1;  // Node failed
    } else {
        return 0;  // Node did not fail
    }
}

void remove_random_node (int number_of_nodes, Node* node) {
    int random_number = rand() % (number_of_nodes);
    printf("Randomly chose node %d to fail\n", random_number);
    node[random_number].add_after_x_jobs = -1;
}

int remove_node_following_failure_rate (int number_of_nodes, Node* node) {
    for (int i = 0; i < number_of_nodes; i++) {
        if (check_if_node_failed(&node[i])) {  
            printf("Node %d failed\n", node[i].id);
            node[i].add_after_x_jobs = -1;
            return 1;
        }
    }
    return 0;
}
