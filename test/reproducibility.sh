# Memory constraint and good nodes
bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 0.999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 0.9999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 0.99999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 0.999999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
python3 plot/mininet/plot_evolution_relibaility_threshold_efficiency_and_size_bars_only.py 10_most_used_nodes_MEVA_merged_365_ _250_max0

# Different set of nodes
bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/most_used_node_x10.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_reliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
python3 plot/mininet/plot_size_stored_and_efficiency_different_set_of_nodes.py _MEVA_merged_365_-1.0_250_max0 only_storage # Only storage
#~ python3 plot/mininet/plot_size_stored_and_efficiency_different_set_of_nodes.py _MEVA_merged_365_-1.0_250_max0 all # Both

# Different datasets
bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/processed_sentinal-2_256351_data.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/IBM_385707_data.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/FB_merged_8337_data.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
python3 plot/mininet/plot_size_stored_and_efficiency_different_datasets.py 10_most_used_nodes_-1 only_storage
#~ python3 plot/mininet/plot_size_stored_and_efficiency_different_datasets.py 10_most_used_nodes_-1 all

# Plot throughput difference figure
python3 plot/mininet/plot_throughput_vs_drex.py _MEVA_merged_365_-1.0_250_max0 

# Stacked times
bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
python3 plot/mininet/stacked_times.py

# With failures
bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 3 0 0 drex/inputs/nodes/10_most_unreliable_nodes_failure_MEVA_merged_250.csv
mv *_times.csv plot/drex_only/10_most_unreliable_nodes_MEVA_merged_365_0.9_250_max0_node_removal/
python3 plot/mininet/event_plot_breaking_point_all_reliability.py 365 drex_only individual drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 0 3

bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 3 0 0 drex/inputs/nodes/10_most_unreliable_nodes_failure_MEVA_merged_250.csv
mv *_times.csv plot/drex_only/10_most_unreliable_nodes_MEVA_merged_365_0.99999_250_max0_node_removal
python3 plot/mininet/event_plot_breaking_point_all_reliability.py 365 drex_only individual drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 0 3

# Scaling
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/most_used_node_x10.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_used_nodesx5.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_used_nodesx10.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/most_used_node_x50.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/

# Time of an algorithm
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 10 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_used_nodesx5.csv drex/inputs/data/MEVA_merged.csv 10 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_used_nodesx10.csv drex/inputs/data/MEVA_merged.csv 10 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
