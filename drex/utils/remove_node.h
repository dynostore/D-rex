#ifndef REMOVE_NODE_H
#define REMOVE_NODE_H

int check_if_node_failed(Node *node);
int remove_random_node (int number_of_nodes, Node* node);
int remove_node_following_failure_rate (int number_of_nodes, Node* node);
void reschedule_lost_chunks(Node* removed_node);

#endif
