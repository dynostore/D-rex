#ifndef REMOVE_NODE_H
#define REMOVE_NODE_H

int check_if_node_failed(Node *node);
int remove_random_node (int number_of_nodes, Node* node, int* removed_node_id);
int remove_node_following_failure_rate (int number_of_nodes, Node* node, int* removed_node_id);
void reschedule_lost_chunks(Node* removed_node, Node* nodes, int number_of_nodes, double* total_remaining_size);

#endif
