#include <stdio.h>
#include <float.h>
#include <stdlib.h>
#include <../schedulers/algorithm4.h>
#include <remove_node.h>
#include <time.h>

void reschedule_lost_chunks() {
    
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

void remove_node_following_failure_rate (int number_of_nodes, Node* node) {
    for (int i = 0; i < number_of_nodes; i++) {
        if (check_if_node_failed(&node[i])) {  
            printf("Node %d failed\n", i);
            node[i].add_after_x_jobs = -1;
        }
    }
}
