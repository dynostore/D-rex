# Done
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv 1500 100000
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_reliable_nodes.csv 1500 100000
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_unreliable_nodes.csv 1500 100000
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/all_nodes_backblaze.csv 3000 100000
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/most_used_node_x10.csv 1500 100000

#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/test.csv 1

#~ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 20
bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 20
bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250
#~ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 20
#~ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 20
#~ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 20
#~ bash test/run_experiments_drex_only.sh 365 0.999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 20
#~ bash test/run_experiments_drex_only.sh 365 0.9999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 20
#~ bash test/run_experiments_drex_only.sh 365 0.99999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 20


#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_reliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250
bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/most_used_node_x10.csv drex/inputs/data/MEVA_merged.csv 250
#~ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/all_nodes_backblaze.csv drex/inputs/data/MEVA_merged.csv 250


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
#   drex/inputs/data/FB_merged  928 TB W 161 TB R 36974 data

#   drex/inputs/data/IBM.csv    3 PB W 111 PB R 45799167 data

#   drex/inputs/data/processed_sentinal-2.csv 13 PB W 29565495 data

#   drex/inputs/data/all_merged.csv 18 PB W 112 PB R

# Or a number of data and their size like
#   100 1000
#   1000 1000
