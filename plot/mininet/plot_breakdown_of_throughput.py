# python3 plot/mininet/plot_breakdown_of_throughput.py

import os
import pandas as pd
import matplotlib.pyplot as plt
import csv
import re
import sys
import numpy as np
from matplotlib.ticker import LogLocator
from functools import partial
import matplotlib.patches as mpatches
from matplotlib.container import BarContainer  # Import BarContainer

def create_folder(folder_path):
    try:
        os.makedirs(folder_path, exist_ok=True)
    except Exception as e:
        print(f"An error occurred: {e}")

# Prompt the user for the folder suffix
# ~ folder_suffix = sys.argv[1]  # This will be the part of the folder name after the set of nodes

# Nice figs
plt.style.use("/home/gonthier/Chicago/paper.mplstyle")
pt = 1./72.27
jour_sizes = {"PRD": {"onecol": 246.*pt, "twocol": 510.*pt},
              "CQG": {"onecol": 374.*pt},}
my_width = jour_sizes["PRD"]["twocol"]
golden = (1 + 5 ** 0.5) / 2
# ~ golden = (1 + 5 ** 0.5) / 1.5 # Smaller height
golden = (1 + 5 ** 0.5) / 2.4 # Higher height
plt.rcParams.update({
    'axes.labelsize': 14,       # Axis label font size
    'legend.fontsize': 14,      # Legend font size
    'xtick.labelsize': 14,      # X-axis tick label font size
})

# ~ data_folder_sentinal = 'plot/drex_only/10_most_used_nodes_processed_sentinal-2_256351_data_365_-1.0_1_max0'
data_folder_small_meva = 'plot/drex_only/10_most_used_nodes_MEVA_merged_365_0.9999_250_max0'
# ~ data_folder_fb = 'plot/drex_only/10_most_used_nodes_FB_merged_8337_data_365_-1.0_1_max0'
# ~ data_folder_ibm = 'plot/drex_only/10_most_used_nodes_IBM_385707_data_365_-1.0_1_max0'
# ~ folder_list = [data_folder_sentinal]
folder_list = [data_folder_small_meva]
# ~ folder_list = [data_folder_sentinal, data_folder_fb, data_folder_ibm]

# Combined plot for 'size_stored' as bars and 'throughput' (renamed from efficiency) as hashed bars
# ~ metric_to_plot_bars = 'size_stored'
# ~ metric_to_plot_efficiency = 'efficiency'


data = []
df_data = []
df = []

# Traverse through each folder
for folder in folder_list:
    # Read all CSV files in the folder
    for file in os.listdir(folder):
        if file.endswith('.csv') and file.startswith('output_drex_only'):
            match = re.search(r'10_most_used_nodes_(.*?)_data', folder)
            # ~ data_set = match.group(1)
            data_set = "MEVA"

            # ~ file_path = os.path.join(folder, file)
            file_path = folder + "/output_drex_only_10_most_used_nodes_MEVA_merged_250.csv"
            print("Reading", file_path)
            df = pd.read_csv(file_path, quotechar='"', doublequote=True, skipinitialspace=True)
            # ~ print(df['size_stored'])
            # ~ df['throughput1'] = df['size_stored'] / (df['total_parralelized_upload_time'])
            df['throughput1'] = df['total_parralelized_upload_time']
            df['throughput2'] =  (df['total_read_time_parrallelized'])

            df['throughput3'] =  (df['total_chunking_time'])
            # ~ df['throughput3'] = df['size_stored'] / (df['total_read_time_parrallelized'])
            df['throughput4'] =  (df['total_reconstruct_time'])
            # ~ df['throughput3'] = 0
            # ~ df['throughput4'] = 0
            print(df['algorithm'])
            print("Uploda")
            print(df['size_stored'] / df['throughput1'])
            print("Read")
            print(df['size_stored'] / df['throughput2'])
            print("Chunking")
            print(df['size_stored'] / df['throughput3'])
            print("Decode")
            print(df['size_stored'] / df['throughput4'])
            print(df['size_stored'] / (df['total_parralelized_upload_time'] + df['total_chunking_time'] + df['total_read_time_parrallelized'] + df['total_reconstruct_time']))
                    
            # Fetch the algorithm names and corresponding values
            for i, algorithm in enumerate(df['algorithm']):
                throughput_value1 = df['throughput1'].iloc[i]
                throughput_value2 = df['throughput2'].iloc[i]
                throughput_value3 = df['throughput3'].iloc[i]
                throughput_value4 = df['throughput4'].iloc[i]
                data.append((data_set, algorithm, throughput_value1, throughput_value2, throughput_value3, throughput_value4))

# Convert the data into a DataFrame
df_data = pd.DataFrame(data, columns=['Data Set', 'Algorithm', 'throughput1', 'throughput2', 'throughput3', 'throughput4'])

# Rename algorithms
df_data['Algorithm'] = df_data['Algorithm'].replace({
    'alg1_c': 'GreedyMinStorage', 'alg4_1': 'D-Rex SC',
    'hdfs_3_replication_c': 'HDFS 3 Rep', 'hdfsrs_3_2': 'EC(3,2)',
    'hdfsrs_6_3': 'EC(6,3)', 'glusterfs_6_4': 'EC(4,2)',
    'Min_Storage_c': 'Min_Storage', 'alg_bogdan': 'D-Rex LB',
    'glusterfs_6_4_c': 'EC(4,2)', 'glusterfs_0_0_c': 'EC(4,2)',
    'GlusterFS_c': 'EC(4,2)', 'hdfs_rs_3_2_c': 'EC(3,2)',
    'hdfs_rs_6_3_c': 'EC(6,3)', 'hdfs_rs_4_2_c': 'HDFS(4,2)',
    'hdfs_rs_0_0_c': 'HDFS_RS_ADAPTATIVE', 'random_c': 'Random',
    'daos_1_0_c': 'DAOS', 'daos_2_0_c': 'DAOS_2R'
})

# ~ # Filter out rows where the value is 0 in the column you want to plot
# ~ df_data = df_data[(df_data['size_stored'] != 0) & (df_data['throughput'] != 0)]

# Filter out some algorithms
algorithms_to_exclude = ['HDFS(4,2)', 'GlusterFS_ADAPTATIVE', 'DAOS_2R', 'HDFS_RS_ADAPTATIVE', 'EC(3,2)', 'EC(4,2)', 'D-Rex LB', 'HDFS 3 Rep']
# ~ order = [0, 2, 1, 3, 4, 5, 7, 6]  # The new order for labels (C first, A second, B third)
order = [0, 1, 2, 3]  # The new order for labels (C first, A second, B third)
# ~ colors = ['#1f77b4', '#ffbf00', '#17becf', '#2ca02c', '#800000', '#d62728', '#ff7f0e', '#7f7f7f']
colors = ['#1f77b4', '#ffbf00', '#17becf', '#2ca02c', '#800000', '#d62728', '#ff7f0e', '#7f7f7f']

filtered_df = df_data[~df_data['Algorithm'].isin(algorithms_to_exclude)]

# ~ print(df['throughput1'])
            # ~ print(df['throughput2'])
            # ~ print(df['throughput3'])
            # ~ print(df['throughput4'])
            # ~ print(df['size_stored'] / (df['total_parralelized_upload_time'] + df['total_chunking_time'] + df['total_read_time_parrallelized'] + df['total_reconstruct_time']))
            
# Separate the data into storage and throughput
# Create the plot with a single subplot (ax)
fig, ax1 = plt.subplots(figsize=(my_width, my_width / golden))

# Create a second Y-axis sharing the same X-axis
ax2 = ax1.twinx()

# Initialize dictionaries for throughput and storage data
throughput_data1 = {}
throughput_data2 = {}
throughput_data3 = {}
throughput_data4 = {}
# ~ storage_data = {}

# Group the DataFrame by 'Set of Nodes'
grouped = filtered_df.groupby('Data Set')

# Get all unique algorithms
unique_algorithms = filtered_df['Algorithm'].unique()

# Iterate over each group
for data_set, group in grouped:
    efficiency_list1 = [np.nan] * len(unique_algorithms)
    efficiency_list2 = [np.nan] * len(unique_algorithms)
    efficiency_list3 = [np.nan] * len(unique_algorithms)
    efficiency_list4 = [np.nan] * len(unique_algorithms)
    storage_list = [np.nan] * len(unique_algorithms)
    
    algorithm_index = {alg: index for index, alg in enumerate(unique_algorithms)}
    
    for _, row in group.iterrows():
        index = algorithm_index[row['Algorithm']]
        # ~ storage_list[index] = row['size_stored']
        efficiency_list1[index] = row['throughput1']
        efficiency_list2[index] = row['throughput2']
        efficiency_list3[index] = row['throughput3']
        efficiency_list4[index] = row['throughput4']
    
    throughput_data1[data_set] = efficiency_list1
    throughput_data2[data_set] = efficiency_list2
    throughput_data3[data_set] = efficiency_list3
    throughput_data4[data_set] = efficiency_list4
    # ~ storage_data[data_set] = storage_list

# ~ bar_width = 0.09
# ~ bar_spacing = 0.3  # Adjust spacing between sets of nodes
bar_width = 0.1  # Adjust the bar width so there’s enough space for 4 bars side by side
bar_spacing = 0.4  # Adjust spacing between sets of nodes

data_set = filtered_df['Data Set'].unique().tolist()
x = np.arange(len(data_set)) * (len(unique_algorithms) * bar_width + bar_spacing)


# ~ # Plot efficiency data on the top subplot
# ~ for i, scheduler in enumerate(unique_algorithms):
    # ~ bars = ax.bar(x + i * bar_width, [throughput_data1[data_se][i] for data_se in data_set], 
                      # ~ width=bar_width, alpha=0.6, label=f'{scheduler}', color=colors[i], edgecolor='black')
    # ~ bars = ax.bar(x + i * bar_width, [throughput_data2[data_se][i] for data_se in data_set], 
                      # ~ width=bar_width, alpha=0.6, label=f'{scheduler}', color=colors[i], edgecolor='black')
    # ~ bars = ax.bar(x + i * bar_width, [throughput_data3[data_se][i] for data_se in data_set], 
                      # ~ width=bar_width, alpha=0.6, label=f'{scheduler}', color=colors[i], edgecolor='black')
    # ~ bars = ax.bar(x + i * bar_width, [throughput_data4[data_se][i] for data_se in data_set], 
                      # ~ width=bar_width, alpha=0.6, label=f'{scheduler}', color=colors[i], edgecolor='black')

# Plot efficiency (throughput) data on the same axis
# ~ for i, scheduler in enumerate(unique_algorithms):
    # ~ print(scheduler)
    # ~ # Adjust the x-position to have 4 bars for each scheduler side by side
    # ~ ax.bar(x + i * (bar_width + bar_spacing), [throughput_data1[data_se][i] for data_se in data_set], 
           # ~ width=bar_width, alpha=0.6, label=f'{scheduler} - Throughput 1', color=colors[i], edgecolor='black')
    
    # ~ ax.bar(x + i * (bar_width + bar_spacing) + bar_width, [throughput_data2[data_se][i] for data_se in data_set], 
           # ~ width=bar_width, alpha=0.6, label=f'{scheduler} - Throughput 2', color=colors[i], edgecolor='black')
    
    # ~ ax.bar(x + i * (bar_width + bar_spacing) + 2 * bar_width, [throughput_data3[data_se][i] for data_se in data_set], 
           # ~ width=bar_width, alpha=0.6, label=f'{scheduler} - Throughput 3', color=colors[i], edgecolor='black')
    
    # ~ ax.bar(x + i * (bar_width + bar_spacing) + 3 * bar_width, [throughput_data4[data_se][i] for data_se in data_set], 
           # ~ width=bar_width, alpha=0.6, label=f'{scheduler} - Throughput 4', color=colors[i], edgecolor='black')

# Plot throughput data for Y-axis 1 (throughput 1 and 2)
for i, scheduler in enumerate(unique_algorithms):
    # Adjust the x-position to have 4 bars for each scheduler side by side
    ax1.bar(x + i * (bar_width + bar_spacing), [throughput_data1[data_se][i] for data_se in data_set], 
            width=bar_width, alpha=0.6, label=f'{scheduler} - Throughput 1', color=colors[i], edgecolor='black')
    
    ax1.bar(x + i * (bar_width + bar_spacing) + bar_width, [throughput_data2[data_se][i] for data_se in data_set], 
            width=bar_width, alpha=0.6, label=f'{scheduler} - Throughput 2', color=colors[i], edgecolor='black')

# Plot throughput data for Y-axis 2 (throughput 3 and 4)
for i, scheduler in enumerate(unique_algorithms):
    ax2.bar(x + i * (bar_width + bar_spacing) + 2 * bar_width, [throughput_data3[data_se][i] for data_se in data_set], 
            width=bar_width, alpha=0.6, label=f'{scheduler} - Throughput 3', color=colors[i], edgecolor='black')
    
    ax2.bar(x + i * (bar_width + bar_spacing) + 3 * bar_width, [throughput_data4[data_se][i] for data_se in data_set], 
            width=bar_width, alpha=0.6, label=f'{scheduler} - Throughput 4', color=colors[i], edgecolor='black')
            
# ~ # Plot storage data on the bottom subplot
# ~ for i, scheduler in enumerate(unique_algorithms):
    # ~ bars = ax_bottom.bar(x + i * bar_width, [storage_data[data_se][i] for data_se in data_set], 
                         # ~ width=bar_width, alpha=0.6, label=f'{scheduler}', color=colors[i], edgecolor='black')

ax1.set_ylabel('Read and write throughput')
# ~ ax2.set_ylabel('Encode and decode throughput')

# Set the limits for the y-axes
# ~ ax1.set_ylim(0, 14)  # Adjust this as per your data for throughput 1 and 2
# ~ ax2.set_ylim(0, 14)  # Adjust this as per your data for throughput 3 and 4

# ~ ax_bottom.set_ylabel('Proportion of Data Sizes Stored (\%)')
# ~ ax.set_ylabel('Throughput')
# ~ ax_bottom.set_xticks(x + bar_width * (len(unique_algorithms) - 1) / 2)
# ~ ax.set_xticks(x + bar_width * (len(unique_algorithms) - 1) / 2)
# Set x-axis labels (algorithm names) under the respective bars
# ~ ax.set_xticks(x + 1.5 * len(unique_algorithms))  # Center the x-ticks between the bars for each algorithm
ax1.set_xticks([0, 0.5, 1, 1.5])
ax1.set_xticklabels(unique_algorithms, rotation=45, ha='right')
# ~ ax_bottom.set_xticklabels(('Sentinal', 'FB', 'IBM'), rotation=0, ha='center')
# ~ ax_bottom.set_ylim(0, 100)
# ~ ax.set_ylim(0, 14)
ax1.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)
# ~ ax_bottom.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)

# Add legends
handles, labels = plt.gca().get_legend_handles_labels()
fig.legend([handles[idx] for idx in order], [labels[idx] for idx in order], loc='lower center', bbox_to_anchor=(0.54, -0.18), fancybox=False, ncol=3)

plt.tight_layout()

# Save the figures as PDFs
plt.savefig("plot/combined/throughput_breakdown_sentinal_most_used.pdf")
