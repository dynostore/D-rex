#ifndef REMOVE_NODE_H
#define REMOVE_NODE_H

int check_if_node_failed(Node *node);
void remove_random_node (int number_of_nodes, Node* node);
void remove_node_following_failure_rate (int number_of_nodes, Node* node);

#endif
