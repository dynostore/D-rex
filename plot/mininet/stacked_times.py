# python3 plot/mininet/stacked_times.py

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import ast

# Nice figs
plt.style.use("/home/gonthier/Chicago/paper.mplstyle")
pt = 1./72.27
jour_sizes = {"PRD": {"onecol": 246.*pt, "twocol": 510.*pt},
              "CQG": {"onecol": 374.*pt},
              "PRDFULLPAGE": {"twocol": 1000.*pt},}
my_width = jour_sizes["PRD"]["twocol"]
golden = (1 + 5 ** 0.5) / 2
# ~ golden = (1 + 5 ** 0.5) / 1.8 # Smaller height
plt.rcParams.update({
    'axes.labelsize': 14,       # Axis label font size
    'legend.fontsize': 14,      # Legend font size
    'xtick.labelsize': 14,      # X-axis tick label font size
})

# Read the CSV file into a pandas DataFrame
file_path = "plot/drex_only/10_most_used_nodes_MEVA_merged_365_0.9999_25_max0/output_drex_only_10_most_used_nodes_MEVA_merged_25.csv"
df = pd.read_csv(file_path, quotechar='"', doublequote=True, skipinitialspace=True)

# Assuming the columns for the different times are like 'chunking_time', 'upload_time', 'read_time', etc.
# You may need to replace these with the actual column names from your dataset.
time_columns = ['total_parralelized_upload_time', 'total_read_time_parrallelized', 'total_chunking_time', 'total_reconstruct_time']

# Initialize a figure for the plot
plt.figure(figsize=(my_width, my_width/(golden)))

# Rename algorithms
df['algorithm'] = df['algorithm'].str.replace('alg1_c', 'GreedyMinStorage')
df['algorithm'] = df['algorithm'].str.replace('alg4_1', 'D-Rex SC')
df['algorithm'] = df['algorithm'].str.replace('hdfs_3_replication_c', 'HDFS 3 Rep')
df['algorithm'] = df['algorithm'].str.replace('hdfsrs_3_2', 'HDFS(3,2)')
df['algorithm'] = df['algorithm'].str.replace('hdfsrs_6_3', 'HDFS(6,3)')
df['algorithm'] = df['algorithm'].str.replace('glusterfs_6_4', 'GlusterFS')
df['algorithm'] = df['algorithm'].str.replace('Min_Storage_c', 'Min_Storage')
df['algorithm'] = df['algorithm'].str.replace('alg_bogdan', 'D-Rex LB')
df['algorithm'] = df['algorithm'].str.replace('glusterfs_6_4_c', 'GlusterFS')
df['algorithm'] = df['algorithm'].str.replace('glusterfs_0_0_c', 'GlusterFS_ADAPTATIVE')
df['algorithm'] = df['algorithm'].str.replace('GlusterFS_c', 'EC(4,2)')
df['algorithm'] = df['algorithm'].str.replace('hdfs_rs_3_2_c', 'EC(3,2)')
df['algorithm'] = df['algorithm'].str.replace('hdfs_rs_6_3_c', 'EC(6,3)')
df['algorithm'] = df['algorithm'].str.replace('hdfs_rs_4_2_c', 'HDFS(4,2)')
df['algorithm'] = df['algorithm'].str.replace('hdfs_rs_0_0_c', 'HDFS_RS_ADAPTATIVE')
df['algorithm'] = df['algorithm'].str.replace('random_c', 'Random')
df['algorithm'] = df['algorithm'].str.replace('daos_1_0_c', 'DAOS')
df['algorithm'] = df['algorithm'].str.replace('daos_2_0_c', 'DAOS_2R')

algorithms_to_exclude = ['HDFS(4,2)', 'GlusterFS_ADAPTATIVE', 'DAOS_2R', 'HDFS_RS_ADAPTATIVE']
filtered_df = df[~df['algorithm'].isin(algorithms_to_exclude)]

# Define fixed colors for each type of operation
colors = {
    'total_parralelized_upload_time': 'skyblue',
    'total_read_time_parrallelized': 'lightgreen',
    'total_chunking_time': 'orange',
    'total_reconstruct_time': 'salmon'
}

# Custom labels for the legend
custom_labels = {
    'total_parralelized_upload_time': 'Parallelized upload',
    'total_read_time_parrallelized': 'Parallelized download',
    'total_chunking_time': 'Encoding',
    'total_reconstruct_time': 'Decoding'
}

# Get a list of unique algorithms from the dataset
algorithms = filtered_df['algorithm'].unique()
print(algorithms)
dividor=60
# Loop through each algorithm and plot the stacked bar for each
for algorithm in algorithms:
    # Filter the dataframe for the current algorithm
    algorithm_df = filtered_df[filtered_df['algorithm'] == algorithm]
    
    # Sum the time columns for the current algorithm
    summed_times = algorithm_df[time_columns].sum()
    
    # Plot the stacked bar for the current algorithm
    plt.bar(algorithm, summed_times['total_parralelized_upload_time']/dividor, label=custom_labels['total_parralelized_upload_time'], bottom=0, color=colors['total_parralelized_upload_time'], edgecolor='black', width=0.7)
    plt.bar(algorithm, summed_times['total_read_time_parrallelized']/dividor, label=custom_labels['total_read_time_parrallelized'], bottom=summed_times['total_parralelized_upload_time']/dividor, color=colors['total_read_time_parrallelized'], edgecolor='black', width=0.7)
    plt.bar(algorithm, summed_times['total_chunking_time']/dividor, label=custom_labels['total_chunking_time'], bottom=summed_times['total_parralelized_upload_time']/dividor + summed_times['total_read_time_parrallelized']/dividor, color=colors['total_chunking_time'] ,edgecolor='black', width=0.7)
    plt.bar(algorithm, summed_times['total_reconstruct_time']/dividor, label=custom_labels['total_reconstruct_time'], bottom=summed_times['total_parralelized_upload_time']/dividor + summed_times['total_read_time_parrallelized']/dividor + summed_times['total_chunking_time']/dividor, color=colors['total_reconstruct_time'], edgecolor='black', width=0.7)
    
# Adding labels and title
# ~ plt.xlabel('algorithm')
plt.ylabel('Hours (h)', fontsize=14)
# ~ plt.title('Stacked Times for Different algorithms')
# Set tick parameters (size for x and y axis)
plt.xticks(fontsize=12, rotation=25, ha="right")
plt.yticks(fontsize=14)
# Reduce the number of y-ticks
max_y = plt.gca().get_ylim()[1]
plt.yticks(ticks=range(0, int(20000) + 1, int(20000 // 5)))  # 5 intervals
# Avoid overlapping legend (show only one legend for each time type)
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
# ~ plt.legend(by_label.values(), by_label.keys(), loc='upper right', bbox_to_anchor=(0.5, -0.4), ncol=2, fontsize=14)
plt.legend(by_label.values(), by_label.keys(), loc='center', bbox_to_anchor=(0.5, -0.64), ncol=2, fontsize=14)
# Display the plot
# ~ plt.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)

plt.tight_layout()  # Adjust layout to prevent clipping of labels
plt.savefig('plot/combined/stacked_times.pdf')
