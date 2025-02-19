# Reproducibility repository for the paper "D-Rex: Adaptive Erasure Coding for Efficient Data Storage on Wide-Area Heterogeneous Storage Systems"

This repository provides the source code, input data, and simulation necessary to reproduce the results presented in the D-Rex paper. You can regenerate the figures and tables from the paper using the provided simulation and plotting scripts.

Clone the repository using the following command:
```bash
~$ git clone -b reproducibility --single-branch https://github.com/dynostore/D-rex.git
```

## Reproducing Results

To reproduce Figures 5, 7, 8, 9 and Tables IV and V, run the following command:
```bash
~/D-rex$ bash test/all_drex_only.sh
```
Results will be generated in the folder: D-rex/plot/combined

## Reproducing Individual Results

### Figure 5:
Run experiments for different reliability thresholds:
```bash
~/D-rex$ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ bash test/run_experiments_drex_only.sh 365 0.999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ bash test/run_experiments_drex_only.sh 365 0.999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ bash test/run_experiments_drex_only.sh 365 0.9999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ bash test/run_experiments_drex_only.sh 365 0.99999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ bash test/run_experiments_drex_only.sh 365 0.999999999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ python3 plot/mininet/plot_evolution_relibaility_threshold_efficiency_and_size_bars_only.py 10_most_used_nodes_MEVA_merged_365_ _250_max0
```

### Figure 7:
Run experiments with different node configurations:
```bash
~/D-rex$ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/most_used_node_x10.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_reliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ python3 plot/mininet/plot_size_stored_and_efficiency_different_set_of_nodes.py _MEVA_merged_365_-1.0_250_max0
```

### Figure 8:
Run experiments to differentiate the different data operations:
```bash
~/D-rex$ bash test/run_experiments_drex_only.sh 365 0.9999 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/MEVA_merged.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ python3 plot/mininet/stacked_times.py
```

### Figure 9:
Run experiments with different datasets:
```bash
~/D-rex$ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/processed_sentinal-2_256351_data.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/IBM_385707_data.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ bash test/run_experiments_drex_only.sh 365 -1 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/FB_merged_8337_data.csv 1 drex/inputs/nodes/no_supplementary_nodes.csv 0 0 0 drex/
~/D-rex$ python3 plot/mininet/plot_size_stored_and_efficiency_different_datasets.py 10_most_used_nodes_-1
```

### Tables IV V:
Run experiments to analyze node failure and reliability:
```bash
~/D-rex$ bash test/run_experiments_drex_only.sh 365 0.9 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 3 0 0 drex/inputs/nodes/10_most_unreliable_nodes_failure_MEVA_merged_250.csv
~/D-rex$ python3 plot/mininet/event_plot_breaking_point_all_reliability.py 365 drex_only individual drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 0 3
~/D-rex$ bash test/run_experiments_drex_only.sh 365 0.99999 drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 drex/inputs/nodes/no_supplementary_nodes.csv 3 0 0 drex/inputs/nodes/10_most_unreliable_nodes_failure_MEVA_merged_250.csv
~/D-rex$ python3 plot/mininet/event_plot_breaking_point_all_reliability.py 365 drex_only individual drex/inputs/nodes/10_most_unreliable_nodes.csv drex/inputs/data/MEVA_merged.csv 250 0 3
```
The standard output then prints the results.


