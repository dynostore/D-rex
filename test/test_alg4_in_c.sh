truncate -s 0 output_drex_only.csv
#~ gcc -Wall drex/schedulers/algorithm4.c -o alg4 -lm
#~ gcc -DPRINT -Wall drex/schedulers/algorithm4.c -o alg4 -lm
#~ ./alg4 drex/inputs/nodes/10_most_reliable_nodes.csv drex/inputs/data/test.csv 365.0 0.99 2
make
#~ ./alg4 drex/inputs/nodes/10_most_reliable_nodes.csv drex/inputs/data/test.csv 365.0 0.99 2 4
#~ ./alg4 drex/inputs/nodes/test.csv drex/inputs/data/test.csv 365.0 0.99 2 3 drex/inputs/nodes/add_node_pattern_1.csv 0 0

./alg4 drex/inputs/nodes/test.csv drex/inputs/data/test.csv 365.0 0.99 2 6 drex/inputs/nodes/add_node_pattern_1.csv 0 0 3 2
./alg4 drex/inputs/nodes/test.csv drex/inputs/data/test.csv 365.0 0.99 2 6 drex/inputs/nodes/add_node_pattern_1.csv 0 0 6 3

#~ ./alg4 drex/inputs/nodes/test.csv drex/inputs/data/test.csv 365.0 0.99 2 4 drex/inputs/nodes/add_node_pattern_1.csv 0 0
#~ ./alg4 drex/inputs/nodes/all_nodes_backblaze.csv drex/inputs/data/test.csv 365.0 0.99 2 4 drex/inputs/nodes/add_node_pattern_1.csv
#~ ./alg4 drex/inputs/nodes/all_nodes_backblaze.csv drex/inputs/data/test.csv 365.0 0.99 2 4 drex/inputs/nodes/no_supplementary_nodes.csv
#~ ./alg4 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/test.csv 365.0 0.99 2 4
#~ ./alg4 drex/inputs/nodes/10_most_reliable_nodes.csv drex/inputs/data/test.csv 365.0 0.99 2 2
#~ ./alg4 drex/inputs/nodes/10_most_reliable_nodes.csv drex/inputs/data/MEVA_merged.csv 365 0.99 2 4
#~ cat output_drex_only.csv
#~ cat output_alg4_stats.csv
#~ cat output_alg2_stats.csv
