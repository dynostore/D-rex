bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv 15000 100000

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
#   drex/inputs/data/MEVA_merged.csv  487 GB W 0 R

#   drex/inputs/data/FB-2009_samples_24_times_1hr_0_withInputPaths.csv  25 TB
#   drex/inputs/data/FB-2010_samples_24_times_1hr_0_withInputPaths.csv  1 PB
#   drex/inputs/data/FB-2009_samples_24_times_1hr_1_withInputPaths.csv  32 TB
#   drex/inputs/data/FB_merged  928 TB W 161 TB R

#   drex/inputs/data/IBM.csv    3 PB W 111 PB R

#   drex/inputs/data/processed_sentinal-2.csv 13 PB W

#   drex/inputs/data/all_merged.csv 18 PB W 112 PB R

# Or a number of data and their size like
#   100 1000
#   1000 1000
