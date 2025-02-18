# No memory constraint and good nodes
#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.9999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.99999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_used_nodes_MEVA_merged_365_ _25_max0

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
#~ # python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_used_nodes_MEVA_merged_365_ _250_max0
#~ # python3 plot/mininet/plot_evolution_relibaility_threshold_efficiency_and_size.py 10_most_used_nodes_MEVA_merged_365_ _250_max0
#~ python3 plot/mininet/plot_evolution_relibaility_threshold_efficiency_and_size_bars_only.py 10_most_used_nodes_MEVA_merged_365_ _250_max0

#~ # Memory constraint and bad nodes
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

#~ # Memory constraint and removing nodes
#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 3 0 0 drex/inputs/nodes/10_most_unreliable_nodes_failure_MEVA_merged_250.csv
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 3 0 0 drex/inputs/nodes/10_most_unreliable_nodes_failure_MEVA_merged_250.csv
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 3 0 0 drex/inputs/nodes/10_most_unreliable_nodes_failure_MEVA_merged_250.csv
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 3 0 0 drex/inputs/nodes/10_most_unreliable_nodes_failure_MEVA_merged_250.csv
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 3 0 0 drex/inputs/nodes/10_most_unreliable_nodes_failure_MEVA_merged_250.csv
#~ python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_unreliable_nodes_MEVA_merged_365_ _250_max0_node_removal
#~ python3 plot/mininet/event_plot_breaking_point_all_reliability.py 365 drex_only individual drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 0 3

# Random reliability given by the user
#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/most_used_node_x10.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_reliable_nodes.csv drex/inputs/data/MEVA_merged.csv 25 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ python3 plot/mininet/plot_size_stored_and_efficiency_different_set_of_nodes.py _MEVA_merged_365_-1.0_25_max0

bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/most_used_node_x10.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_reliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
python3 plot/mininet/plot_size_stored_and_efficiency_different_set_of_nodes.py _MEVA_merged_365_-1.0_250_max0
