#  Usage: <input_node> <input_data> <data_duration_on_system> <reliability_threshold> <number_of_repetition> <algorithm> <input_supplementary_node> <remove_node_pattern> <fixed_random_seed> <max_N>

# Best fit can only work when all data are stored. 3 is the maximum and the goal to reach.
# Efficiency can work in any case vbut tell a different story of course if not all data have been stored, the goal is to be as high as possible

# Test campaign 1: normal
# No memory constraint and good nodes
#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.9999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_used_nodes_MEVA_merged_365_ _25_max0
#~ python3 plot/mininet/plot_evolution_relibaility_threshold_efficiency_and_size.py 10_most_used_nodes_MEVA_merged_365_ _25_max0

# No memory constraint and bad nodes
#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.9999999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99999999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999999999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_unreliable_nodes_MEVA_merged_365_ _25_max0
#~ python3 plot/mininet/plot_evolution_relibaility_threshold_efficiency_and_size.py 10_most_unreliable_nodes_MEVA_merged_365_ _25_max0

# Memory constraint and good nodes
#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.9999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_used_nodes_MEVA_merged_365_ _250_max0
#~ python3 plot/mininet/plot_evolution_relibaility_threshold_efficiency_and_size.py 10_most_used_nodes_MEVA_merged_365_ _250_max0

# Memory constraint and homogeneous nodes
#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/most_used_node_x10.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/most_used_node_x10.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/most_used_node_x10.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/most_used_node_x10.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/most_used_node_x10.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ python3 plot/mininet/plot_evolution_relibaility_threshold.py most_used_node_x10_MEVA_merged_365_ _250_max0

# Memory constraint and bad nodes
#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.9999999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99999999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999999999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_unreliable_nodes_MEVA_merged_365_ _250_max0
#~ python3 plot/mininet/plot_evolution_relibaility_threshold_efficiency_and_size.py 10_most_unreliable_nodes_MEVA_merged_365_ _250_max0

# No memory constraint and all nodes
#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/all_nodes_backblaze.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0
#~ python3 plot/mininet/plot_evolution_relibaility_threshold.py all_nodes_backblaze_MEVA_merged_365_ _250_max0

# Test campaign 2: removing nodes
# Memory constraint and bad nodes
#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 3 0 0 drex/inputs/nodes/10_most_unreliable_nodes_failure_MEVA_merged_250.csv
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 3 0 0 drex/inputs/nodes/10_most_unreliable_nodes_failure_MEVA_merged_250.csv
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 3 0 0 drex/inputs/nodes/10_most_unreliable_nodes_failure_MEVA_merged_250.csv
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 3 0 0 drex/inputs/nodes/10_most_unreliable_nodes_failure_MEVA_merged_250.csv
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 3 0 0 drex/inputs/nodes/10_most_unreliable_nodes_failure_MEVA_merged_250.csv
#~ python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_unreliable_nodes_MEVA_merged_365_ _250_max0_node_removal
#~ python3 plot/mininet/event_plot_breaking_point_all_reliability.py 365 drex_only individual drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 0 3

# Test campaign 3: random reliability given by the user
#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash ../Chicago/compare.sh output_drex_only.csv plot/drex_only/10_most_used_nodes_MEVA_merged_365_-1.0_25_max0/output_drex_only_10_most_used_nodes_MEVA_merged_25.csv
#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash ../Chicago/compare.sh output_drex_only.csv plot/drex_only/10_most_unreliable_nodes_MEVA_merged_365_-1.0_25_max0/output_drex_only_10_most_unreliable_nodes_MEVA_merged_25.csv
#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/most_used_node_x10.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash ../Chicago/compare.sh output_drex_only.csv plot/drex_only/most_used_node_x10_MEVA_merged_365_-1.0_25_max0/output_drex_only_most_used_node_x10_MEVA_merged_25.csv
#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_reliable_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash ../Chicago/compare.sh output_drex_only.csv plot/drex_only/10_most_reliable_nodes_MEVA_merged_365_-1.0_25_max0/output_drex_only_10_most_reliable_nodes_MEVA_merged_25.csv
#~ python3 plot/mininet/plot_size_stored_and_efficiency_different_set_of_nodes.py _MEVA_merged_365_-1.0_25_max0

#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodesx1.5.csv drex/inputs/data/MEVA_merged.csv 325 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash ../Chicago/compare.sh output_drex_only.csv plot/drex_only/10_most_used_nodes_MEVA_merged_365_-1.0_250_max0/output_drex_only_10_most_used_nodes_MEVA_merged_250.csv
#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash ../Chicago/compare.sh output_drex_only.csv plot/drex_only/10_most_unreliable_nodes_MEVA_merged_365_-1.0_250_max0/output_drex_only_10_most_unreliable_nodes_MEVA_merged_250.csv
#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/most_used_node_x10.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash ../Chicago/compare.sh output_drex_only.csv plot/drex_only/most_used_node_x10_MEVA_merged_365_-1.0_250_max0/output_drex_only_most_used_node_x10_MEVA_merged_250.csv
#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_reliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash ../Chicago/compare.sh output_drex_only.csv plot/drex_only/10_most_reliable_nodes_MEVA_merged_365_-1.0_250_max0/output_drex_only_10_most_reliable_nodes_MEVA_merged_250.csv
#~ python3 plot/mininet/plot_size_stored_and_efficiency_different_set_of_nodes.py _MEVA_merged_365_-1.0_250_max0

# Test campaign 4: adding nodes dynamically
#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/add_node_pattern_MEVA_merged_250.csv 0 0 0 drex/

# Test campaing 5: other databases too long will need to cut them before the end one way or another
#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/processed_sentinal-2_256351_data.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash ../Chicago/compare.sh output_drex_only.csv plot/drex_only/10_most_used_nodes_processed_sentinal-2_256351_data_365_-1.0_1_max0/output_drex_only_10_most_used_nodes_processed_sentinal-2_256351_data_1.csv
#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/IBM_385707_data.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash ../Chicago/compare.sh output_drex_only.csv plot/drex_only/10_most_used_nodes_IBM_385707_data_365_-1.0_1_max0/output_drex_only_10_most_used_nodes_IBM_385707_data_1.csv
#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/FB_merged_8337_data.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash ../Chicago/compare.sh output_drex_only.csv plot/drex_only/10_most_used_nodes_FB_merged_8337_data_365_-1.0_1_max0/output_drex_only_10_most_used_nodes_FB_merged_8337_data_1.csv
#~ python3 plot/mininet/plot_size_stored_and_efficiency_different_datasets.py 10_most_used_nodes_-1

# Traces for Dante
#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/8_nodes_from_chicago.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/8_nodes_from_chicago.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/8_nodes_from_chicago.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/

#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_nodes_from_chicago.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_nodes_from_chicago.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_nodes_from_chicago.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/

#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_nodes_from_chicago_campaign2.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_nodes_from_chicago_campaign2.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_nodes_from_chicago_campaign2.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/





# Done
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv 1500 100000
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_reliable_nodes.csv 1500 100000
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_unreliable_nodes.csv 1500 100000
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/all_nodes_backblaze.csv 3000 100000
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/most_used_node_x10.csv 1500 100000

#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/test.csv 1 drex/inputs/nodes/add_node_pattern_1.csv 0 0 0

#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/test.csv 20 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/test.csv 1 drex/inputs/nodes/add_node_pattern_1.csv 0 0 0
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 20
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 20
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 20
#~ bash test/run_experiments_drex_only.sh 365 0.999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 20
#~ bash test/run_experiments_drex_only.sh 365 0.9999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 20
#~ bash test/run_experiments_drex_only.sh 365 0.99999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 20


#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_reliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0
#~ python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_unreliable_nodes_MEVA_merged_365_ _250_max0

#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0
#~ python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_used_nodes_MEVA_merged_365_ _250_max0

#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/most_used_node_x10.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/all_nodes_backblaze.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv


#~ play with values of failure of nodes or use node failure rate
#~ scale how bad you can make your system
#~ show a breaking point of how many data are lost in case of node failure over time per strategy

#~ you are uploading the data, what happen if it fails during that time ? You loose the data because you are moving it

#~ Test with SSds and shiw the difference?

#~ add new node

# Examples
# bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/test.csv

# Options for data duration on system
#   365
#   730
#   3650

# Options for reliability threshold
#   0.9
#   0.99
#   0.999
#   0.9999
#   0.99999999999 (aws 11 nines)

# Options for input nodes:
#   drex/inputs/nodes/10_most_reliable_nodes.csv 122 TB 0.5100 AFR
#   drex/inputs/nodes/10_most_unreliable_nodes.csv 112 TB 6.4790 AFR
#   drex/inputs/nodes/10_most_used_nodes.csv 120 TB 1.2390 AFR
#   drex/inputs/nodes/all_nodes_backblaze.csv 354 TB 2.7487 AFR
#   drex/inputs/nodes/most_used_node_x10.csv 140 TB 0.9700 AFR

# Options for input data:
#   drex/inputs/data/MEVA2.csv  27 GB
#   drex/inputs/data/MEVA1.csv  459 GB
#   drex/inputs/data/MEVA_merged.csv  487 GB W 0 R 4157 data

#   drex/inputs/data/FB-2009_samples_24_times_1hr_0_withInputPaths.csv  25 TB
#   drex/inputs/data/FB-2010_samples_24_times_1hr_0_withInputPaths.csv  1 PB
#   drex/inputs/data/FB-2009_samples_24_times_1hr_1_withInputPaths.csv  32 TB
#   drex/inputs/data/FB_merged  928 TB W 161 TB R 36974 data Cut at 8337 for 122 TB

#   drex/inputs/data/IBM.csv    3 PB W 111 PB R 45799167 data Cut at 385707 for 122TB

#   drex/inputs/data/processed_sentinal-2.csv 13 PB W 29565495 data Cut at 256351 for 122 TB

#   drex/inputs/data/all_merged.csv 18 PB W 112 PB R

# Or a number of data and their size like
#   100 1000
#   1000 1000
