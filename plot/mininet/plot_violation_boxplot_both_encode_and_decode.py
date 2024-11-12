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

    # Define file names and labels
    filenames = [
        'alg4_1.csv', 'alg1_c.csv', 'alg_bogdan.csv', 'hdfs_3_replication_c.csv',
        'hdfs_rs_3_2_c.csv', 'hdfs_rs_6_3_c.csv', 'gluster_fs_6_4_c.csv', 'daos_1_0_c.csv'
    ]
    labels = ['D-Rex SC', 'GreedyMinStorage', 'D-Rex LB', 'HDFS 3 Rep', 
              'EC(3,2)', 'EC(6,3)', 'EC(4,2)', 'DAOS']
    colors = ['#1f77b4', '#ffbf00', '#17becf', '#2ca02c', '#800000', '#d62728', '#ff7f0e', '#7f7f7f']

    # Data structures for storing write and read throughput
    write_data = {label: [] for label in labels}
    read_data = {label: [] for label in labels}
    optimal_write_throughputs = []
    optimal_read_throughputs = []
    
    def compute_write_read_throughput(df):
        df['Reconstruct_Time'] = df['Reconstruct_Time'].replace([np.inf, -np.inf], 0)
        df['Chunking_Time'] = df['Chunking_Time'].replace([np.inf, -np.inf], 0)
        
        write_throughput = df['Size'] / (df['Transfer_Time_Parralelized'] + df['Chunking_Time'])
        read_throughput = df['Size'] / (df['Read_Time_Parralelized'] + df['Reconstruct_Time'])
        
        return write_throughput - threshold, read_throughput - threshold

    for folder_path in folder_paths:
        for filename, label in zip(filenames, labels):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                data = pd.read_csv(file_path)
                write_diff, read_diff = compute_write_read_throughput(data)
                write_data[label].extend(write_diff.replace([np.inf, -np.inf], np.nan).dropna())
                read_data[label].extend(read_diff.replace([np.inf, -np.inf], np.nan).dropna())
        
        optimal_file_path = os.path.join(folder_path, 'optimal_schedule.csv')
        if os.path.isfile(optimal_file_path):
            optimal_data = pd.read_csv(optimal_file_path)
            optimal_write, optimal_read = compute_write_read_throughput(optimal_data)
            optimal_write_throughputs.extend(optimal_write.replace([np.inf, -np.inf], np.nan).dropna())
            optimal_read_throughputs.extend(optimal_read.replace([np.inf, -np.inf], np.nan).dropna())

    mean_optimal_write = np.mean(optimal_write_throughputs)
    mean_optimal_read = np.mean(optimal_read_throughputs)

    # Prepare data for combined boxplot
    combined_data = []
    combined_labels = []
    
    plt.figure(figsize=(my_width, my_width / golden))
    
    # Adding boxplots for each algorithm with color for write and hatch for read
    for i, label in enumerate(labels):
        # Write throughput boxplot
        write_box = plt.boxplot(write_data[label], positions=[i * 2], widths=0.6,
                                patch_artist=True, showfliers=False, manage_ticks=False)
        for patch in write_box['boxes']:
            patch.set_facecolor(colors[i])

        # Read throughput boxplot with hatch
        read_box = plt.boxplot(read_data[label], positions=[i * 2 + 1], widths=0.6,
                               patch_artist=True, showfliers=False, manage_ticks=False)
        for patch in read_box['boxes']:
            patch.set_facecolor(colors[i])
            patch.set_hatch('//')

        combined_labels.extend([f"{label} (Write)", f"{label} (Read)"])
    
        for median in write_box['medians']:
            median.set(color='black', linewidth=3)
        for median in read_box['medians']:
            median.set(color='black', linewidth=3)

    plt.xticks(np.arange(0, len(labels) * 2, 2) + 0.5, labels, rotation=25)
    plt.ylabel('Throughput (MB/s)')

    # ~ # Add horizontal lines for optimal throughput
    # ~ plt.axhline(mean_optimal_write - threshold, color='blue', linestyle='--', linewidth=1.5, label='Mean Optimal Write Throughput')
    # ~ plt.axhline(mean_optimal_read - threshold, color='green', linestyle='--', linewidth=1.5, label='Mean Optimal Read Throughput')
    plt.legend()
    
    plt.tight_layout()
    plt.grid()
    plt.savefig(f"plot/combined/write_read_violation_from_throughput_threshold_of_{threshold}.pdf")

folder_paths = sys.argv[1:5]  # Accept up to 4 folder paths from command line arguments
plot_throughput_boxplots(folder_paths, threshold=12)
