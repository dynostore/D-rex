import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys

def plot_throughput_boxplots(folder_path, threshold=10):
    # Nice figs
    plt.style.use("/home/gonthier/Chicago/paper.mplstyle")
    pt = 1./72.27
    jour_sizes = {"PRD": {"onecol": 246.*pt, "twocol": 510.*pt},
                  "CQG": {"onecol": 374.*pt},}
    my_width = jour_sizes["PRD"]["twocol"]
    # ~ golden = (1 + 5 ** 0.5) / 2
    golden = (1 + 5 ** 0.5) / 1.8
    plt.rcParams.update({
        'axes.labelsize': 14,       # Axis label font size
        'legend.fontsize': 14,      # Legend font size
        'xtick.labelsize': 10,      # X-axis tick label font size
    })

    # Define file paths
    file1_path = os.path.join(folder_path, 'alg4_1.csv')
    file2_path = os.path.join(folder_path, 'alg1_c.csv')
    file3_path = os.path.join(folder_path, 'alg_bogdan.csv')
    file4_path = os.path.join(folder_path, 'hdfs_3_replication_c.csv')
    file5_path = os.path.join(folder_path, 'hdfs_rs_3_2_c.csv')
    file6_path = os.path.join(folder_path, 'hdfs_rs_6_3_c.csv')
    file7_path = os.path.join(folder_path, 'gluster_fs_6_4_c.csv')
    file8_path = os.path.join(folder_path, 'daos_1_0_c.csv')

    # Load data
    data1 = pd.read_csv(file1_path)
    data2 = pd.read_csv(file2_path)
    data3 = pd.read_csv(file3_path)
    data4 = pd.read_csv(file4_path)
    data5 = pd.read_csv(file5_path)
    data6 = pd.read_csv(file6_path)
    data7 = pd.read_csv(file7_path)
    data8 = pd.read_csv(file8_path)
    # ~ print(data1)
    # Define a function to calculate the difference from threshold
    def compute_throughput_difference(df):
        # Replace infinity values in 'Reconstruct_Time' with 0
        df['Reconstruct_Time'] = df['Reconstruct_Time'].replace([np.inf, -np.inf], 0)
        df['Chunking_Time'] = df['Chunking_Time'].replace([np.inf, -np.inf], 0)
        
        # Calculate throughput
        df['Throughput'] = df['Size'] / (df['Transfer_Time_Parralelized'] + df['Chunking_Time'] +
                                         df['Read_Time_Parralelized'] + df['Reconstruct_Time'])
        
        # Calculate the difference from threshold
        df['Difference_From_Threshold'] = df['Throughput'] - threshold
        # ~ print(df['Difference_From_Threshold'])
        return df['Difference_From_Threshold']
    
    # Compute throughput differences for both files
    diff1 = compute_throughput_difference(data1)
    diff2 = compute_throughput_difference(data2)
    diff3 = compute_throughput_difference(data3)
    diff4 = compute_throughput_difference(data4)
    diff5 = compute_throughput_difference(data5)
    diff6 = compute_throughput_difference(data6)
    diff7 = compute_throughput_difference(data7)
    diff8 = compute_throughput_difference(data8)
    # ~ print(diff1.isna().sum())  # Count NaNs in the first dataset
    diff1 = diff1.replace([np.inf, -np.inf], np.nan).dropna()
    diff2 = diff2.replace([np.inf, -np.inf], np.nan).dropna()
    diff3 = diff3.replace([np.inf, -np.inf], np.nan).dropna()
    diff4 = diff4.replace([np.inf, -np.inf], np.nan).dropna()
    diff5 = diff5.replace([np.inf, -np.inf], np.nan).dropna()
    diff6 = diff6.replace([np.inf, -np.inf], np.nan).dropna()
    diff7 = diff7.replace([np.inf, -np.inf], np.nan).dropna()
    diff8 = diff8.replace([np.inf, -np.inf], np.nan).dropna()
    # Combine differences for boxplot
    boxplot_data = [diff1, diff2, diff3, diff4, diff5, diff6, diff7, diff8]
    # ~ boxplot_data = [diff3]
    # ~ print(boxplot_data)
    # Plot boxplot
    plt.figure(figsize=(my_width, my_width/(golden)))
    box = plt.boxplot(boxplot_data, labels=['D-Rex SC', 'GreedyMinStorage', 'D-Rex LB', 'HDFS 3 Rep', 'EC(3,2)', 'EC(6,3)', 'EC(4,2)', 'DAOS'], showmeans = False, patch_artist = True, showfliers=False)
    # ~ box = plt.boxplot(boxplot_data, labels=['D-Rex SC'], showmeans = False, patch_artist = True, showfliers=False)
    plt.xticks(rotation=25)
    
    for median in box['medians']:
        median.set(color='black', linewidth=3)
    
    # Set colors
    colors = ['#1f77b4', '#ffbf00', '#17becf', '#2ca02c', '#800000', '#d62728', '#ff7f0e', '#7f7f7f']
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
    
    # Customize y-axis tick labels
    yticks = plt.yticks()[0]  # Get current y-tick locations
    ytick_labels = [f"{threshold + (y * 3):.1f}" for y in yticks]  # Offset each tick by 3 units

    plt.yticks(yticks, ytick_labels)  # Set new y-tick labels
    
    # ~ plt.axhline(0, color='red', linestyle='--', linewidth=1, label=f'Throughput Threshold')
    # ~ plt.axhline(0, color='red', linestyle='--', linewidth=1)
    plt.ylabel('Throughput (MB/s)')
    # ~ plt.legend()
    to_print = os.path.basename(os.path.normpath(folder_path))
    plt.savefig(f"plot/combined/{to_print}_violation_from_throughput_threshold_of_{threshold}.pdf")

# Usage
folder_path = sys.argv[1]
plot_throughput_boxplots(folder_path, threshold=12) # threshold for throughput
