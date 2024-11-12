import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

def plot_throughput_boxplots(folder_paths, threshold=10):
    plt.style.use("/home/gonthier/Chicago/paper.mplstyle")
    pt = 1./72.27
    jour_sizes = {"PRD": {"onecol": 246.*pt, "twocol": 510.*pt}}
    my_width = jour_sizes["PRD"]["twocol"]
    golden = (1 + 5 ** 0.5) / 1.8
    plt.rcParams.update({
        'axes.labelsize': 14,
        'legend.fontsize': 14,
        'xtick.labelsize': 10,
    })

    # Define file names expected in each folder
    filenames = [
        'alg4_1.csv', 'alg1_c.csv', 'alg_bogdan.csv', 'hdfs_3_replication_c.csv',
        'hdfs_rs_3_2_c.csv', 'hdfs_rs_6_3_c.csv', 'gluster_fs_6_4_c.csv', 'daos_1_0_c.csv'
    ]
    labels = ['D-Rex SC', 'GreedyMinStorage', 'D-Rex LB', 'HDFS 3 Rep', 
              'EC(3,2)', 'EC(6,3)', 'EC(4,2)', 'DAOS']

    # Initialize list to collect throughput differences across folders
    aggregated_data = {label: [] for label in labels}
    optimal_throughputs = []
    
    # Define a function to calculate throughput difference
    def compute_throughput_difference(df):
        df['Reconstruct_Time'] = df['Reconstruct_Time'].replace([np.inf, -np.inf], 0)
        df['Chunking_Time'] = df['Chunking_Time'].replace([np.inf, -np.inf], 0)
        df['Throughput'] = df['Size'] / (df['Transfer_Time_Parralelized'] + df['Chunking_Time'] +
                                         df['Read_Time_Parralelized'] + df['Reconstruct_Time'])
        return df['Throughput'] - threshold

    # Process each folder and each file
    for folder_path in folder_paths:
        # Process the main files
        for filename, label in zip(filenames, labels):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                data = pd.read_csv(file_path)
                diff = compute_throughput_difference(data).replace([np.inf, -np.inf], np.nan).dropna()
                aggregated_data[label].extend(diff)
        
        # Process the optimal_schedule file for mean throughput
        optimal_file_path = os.path.join(folder_path, 'optimal_schedule.csv')
        if os.path.isfile(optimal_file_path):
            optimal_data = pd.read_csv(optimal_file_path)
            optimal_throughput = (optimal_data['Size'] / (optimal_data['Transfer_Time_Parralelized'] + 
                                                          optimal_data['Chunking_Time'] +
                                                          optimal_data['Read_Time_Parralelized'] + 
                                                          optimal_data['Reconstruct_Time']))
            optimal_throughputs.extend(optimal_throughput.replace([np.inf, -np.inf], np.nan).dropna())

    # Compute the mean optimal throughput
    mean_optimal_throughput = np.mean(optimal_throughputs)
    boxplot_data = [aggregated_data[label] for label in labels]
    
    plt.figure(figsize=(my_width, my_width / golden))
    box = plt.boxplot(boxplot_data, labels=labels, showmeans=False, patch_artist=True, showfliers=False)
    plt.xticks(rotation=25)
    
    for median in box['medians']:
        median.set(color='black', linewidth=3)

    colors = ['#1f77b4', '#ffbf00', '#17becf', '#2ca02c', '#800000', '#d62728', '#ff7f0e', '#7f7f7f']
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)

    yticks = plt.yticks()[0]
    ytick_labels = [f"{threshold + (y * 3):.1f}" for y in yticks]
    plt.yticks(yticks, ytick_labels)
    plt.ylabel('Throughput (MB/s)')

    # Add horizontal line for mean optimal throughput
    plt.axhline(mean_optimal_throughput - threshold, color='blue', linestyle='--', linewidth=1.5, label='Mean Optimal Throughput')
    plt.legend()
    plt.grid()
    plt.savefig(f"plot/combined/all_dataset_violation_from_throughput_threshold_of_{threshold}.pdf")

folder_paths = sys.argv[1:5]  # Accept up to 4 folder paths from command line arguments
plot_throughput_boxplots(folder_paths, threshold=12)
