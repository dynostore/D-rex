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
folder_suffix1 = sys.argv[1]  
folder_suffix2 = sys.argv[2]

if folder_suffix1 == "_MEVA_merged_365_-1.0_25_max0":
    total_possible_size_to_store1 = 487000*25
elif folder_suffix1 == "_MEVA_merged_365_-1.0_250_max0":
    total_possible_size_to_store1 = 487000*250
elif folder_suffix1 == "_FB_merged_365_-1.0_1_max0":
    total_possible_size_to_store1 = 928000000*1
else:
    print("Error suffix", folder_suffix1, "not known")
    exit(1)
if folder_suffix2 == "_MEVA_merged_365_-1.0_25_max0":
    total_possible_size_to_store2 = 487000*25
elif folder_suffix2 == "_MEVA_merged_365_-1.0_250_max0":
    total_possible_size_to_store2 = 487000*250
elif folder_suffix2 == "_FB_merged_365_-1.0_1_max0":
    total_possible_size_to_store2 = 928000000*1
else:
    print("Error suffix", folder_suffix2, "not known")
    exit(1)

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

base_dir = 'plot/drex_only'
set_of_node_regex1 = re.compile(r'^(.+)' + re.escape(folder_suffix1) + r'$')
set_of_node_regex2 = re.compile(r'^(.+)' + re.escape(folder_suffix2) + r'$')

# Data storage
data_suffix1 = []
data_suffix2 = []

metric_to_plot_bars = 'size_stored'
metric_to_plot_efficiency = 'efficiency'

colors = ['#1f77b4', '#ffbf00', '#17becf', '#2ca02c', '#800000', '#d62728', '#ff7f0e', '#7f7f7f']
order = [0, 2, 1, 3, 4, 5, 7, 6]

data1 = []
df_data1 = []
df1 = []

# Traverse through each folder
for folder in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder)
    if os.path.isdir(folder_path):
        match = set_of_node_regex1.search(folder)
        if match:
            print(folder_path)
            set_of_nodes = match.group(1)
            print(f"Set of nodes: {set_of_nodes}")
            
            # Get optimal data
            with open(folder_path + "/output_optimal_schedule.csv", mode='r') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)
                for row in csv_reader:
                    number_of_data_stored_optimal = int(row[0])
                    total_storage_used_optimal = float(row[1])
                    best_upload_time_optimal = float(row[2])
                    best_read_time_optimal = float(row[3])
                    size_stored_optimal = float(row[4])

            # Read all CSV files in the folder
            for file in os.listdir(folder_path):
                if file.endswith('.csv') and file.startswith('output_drex_only'):
                    file_path = os.path.join(folder_path, file)
                    df1 = pd.read_csv(file_path, quotechar='"', doublequote=True, skipinitialspace=True)
                    
                    # Calculate throughput (renamed from efficiency)
                    df1['throughput'] = df1['size_stored'] / (df1['total_parralelized_upload_time'] + df1['total_chunking_time'] + df1['total_read_time_parrallelized'] + df1['total_reconstruct_time'])
                    
                    # Fetch the algorithm names and corresponding values
                    for i, algorithm in enumerate(df1['algorithm']):
                        size_stored_value = (df1[metric_to_plot_bars].iloc[i] * 100) / total_possible_size_to_store1
                        throughput_value = df1['throughput'].iloc[i]
                        data1.append((set_of_nodes, algorithm, size_stored_value, throughput_value))
data2 = []
df_data2 = []
df2 = []

# Traverse through each folder
for folder in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder)
    if os.path.isdir(folder_path):
        match = set_of_node_regex2.search(folder)
        if match:
            print(folder_path)
            set_of_nodes = match.group(1)
            print(f"Set of nodes: {set_of_nodes}")
            
            # Get optimal data
            with open(folder_path + "/output_optimal_schedule.csv", mode='r') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)
                for row in csv_reader:
                    number_of_data_stored_optimal = int(row[0])
                    total_storage_used_optimal = float(row[1])
                    best_upload_time_optimal = float(row[2])
                    best_read_time_optimal = float(row[3])
                    size_stored_optimal = float(row[4])

            # Read all CSV files in the folder
            for file in os.listdir(folder_path):
                if file.endswith('.csv') and file.startswith('output_drex_only'):
                    file_path = os.path.join(folder_path, file)
                    df2 = pd.read_csv(file_path, quotechar='"', doublequote=True, skipinitialspace=True)
                    
                    # Calculate throughput (renamed from efficiency)
                    df2['throughput'] = df2['size_stored'] / (df2['total_parralelized_upload_time'] + df2['total_chunking_time'] + df2['total_read_time_parrallelized'] + df2['total_reconstruct_time'])
                    
                    # Fetch the algorithm names and corresponding values
                    for i, algorithm in enumerate(df2['algorithm']):
                        size_stored_value = (df2[metric_to_plot_bars].iloc[i] * 100) / total_possible_size_to_store2
                        throughput_value = df2['throughput'].iloc[i]
                        data2.append((set_of_nodes, algorithm, size_stored_value, throughput_value))


# Convert the data into a DataFrame
df_data1 = pd.DataFrame(data1, columns=['Set of Nodes', 'Algorithm', 'size_stored', 'throughput'])
df_data2 = pd.DataFrame(data2, columns=['Set of Nodes', 'Algorithm', 'size_stored', 'throughput'])

# Rename algorithms
df_data1['Algorithm'] = df_data1['Algorithm'].replace({
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
# Rename algorithms
df_data2['Algorithm'] = df_data2['Algorithm'].replace({
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

# Filter out rows where the value is 0 in the column you want to plot
df_data1 = df_data1[(df_data1['size_stored'] != 0) & (df_data1['throughput'] != 0)]
df_data2 = df_data2[(df_data2['size_stored'] != 0) & (df_data2['throughput'] != 0)]

# Filter out some algorithms
algorithms_to_exclude = ['HDFS(4,2)', 'GlusterFS_ADAPTATIVE', 'DAOS_2R', 'HDFS_RS_ADAPTATIVE']
filtered_df1 = df_data1[~df_data1['Algorithm'].isin(algorithms_to_exclude)]
filtered_df2 = df_data2[~df_data1['Algorithm'].isin(algorithms_to_exclude)]

# Separate the data into storage and throughput

fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(my_width, my_width/(golden)), sharex=True, gridspec_kw={'height_ratios': [1, 1]})

bar_width = 0.09
bar_spacing = 0.3  # Adjust spacing between sets of nodes

# Initialize dictionaries for throughput and storage data
throughput_data1 = {}
storage_data1 = {}
throughput_data2 = {}
storage_data2 = {}

# Group the DataFrame by 'Set of Nodes'
grouped1 = filtered_df1.groupby('Set of Nodes')
grouped2 = filtered_df2.groupby('Set of Nodes')

# Get all unique algorithms
unique_algorithms = filtered_df1['Algorithm'].unique()

# Iterate over each group
for set_of_nodes, group in grouped1:
    efficiency_list = [np.nan] * len(unique_algorithms)
    storage_list = [np.nan] * len(unique_algorithms)
    
    algorithm_index = {alg: index for index, alg in enumerate(unique_algorithms)}
    
    for _, row in group.iterrows():
        index = algorithm_index[row['Algorithm']]
        storage_list[index] = row['size_stored']
        efficiency_list[index] = row['throughput']
    
    throughput_data1[set_of_nodes] = efficiency_list
    storage_data1[set_of_nodes] = storage_list
# Iterate over each group
for set_of_nodes, group in grouped2:
    efficiency_list = [np.nan] * len(unique_algorithms)
    storage_list = [np.nan] * len(unique_algorithms)
    
    algorithm_index = {alg: index for index, alg in enumerate(unique_algorithms)}
    
    for _, row in group.iterrows():
        index = algorithm_index[row['Algorithm']]
        storage_list[index] = row['size_stored']
        efficiency_list[index] = row['throughput']
    
    throughput_data2[set_of_nodes] = efficiency_list
    storage_data2[set_of_nodes] = storage_list

sets_of_nodes = filtered_df1['Set of Nodes'].unique().tolist()
x = np.arange(len(sets_of_nodes)) * (len(unique_algorithms) * bar_width + bar_spacing)

# ~ # Plot efficiency data on the top subplot
# ~ for i, scheduler in enumerate(unique_algorithms):
    # ~ bars = ax_top.bar(x + i * bar_width, [throughput_data1[set_of_node][i] for set_of_node in sets_of_nodes], 
                      # ~ width=bar_width, alpha=0.6, label=f'{scheduler}', color=colors[i], edgecolor='black', hatch='//')
# Plot efficiency data on the top subplot
for i, scheduler in enumerate(unique_algorithms):
    bars = ax_top.bar(x + i * bar_width, [storage_data1[set_of_node][i] for set_of_node in sets_of_nodes], 
                      width=bar_width, alpha=0.6, label=f'{scheduler}', color=colors[i], edgecolor='black')

# Plot storage data on the bottom subplot
for i, scheduler in enumerate(unique_algorithms):
    bars = ax_bottom.bar(x + i * bar_width, [storage_data2[set_of_node][i] for set_of_node in sets_of_nodes], 
                         width=bar_width, alpha=0.6, label=f'{scheduler}', color=colors[i], edgecolor='black')


# Set labels and limits
# Remove individual y-axis labels
# Set y-axis labels
ax_top.set_ylabel('Non-saturating workload')
ax_bottom.set_ylabel('Saturating workload')

# Move labels to the right
ax_top.yaxis.set_label_position('right')
ax_bottom.yaxis.set_label_position('right')
# Add a shared y-axis label for the entire figure
fig.text(-0.01, 0.5, 'Proportion of Data Sizes Stored (\%)', va='center', rotation='vertical', fontsize=14)

ax_bottom.set_xticks(x + bar_width * (len(unique_algorithms) - 1) / 2)
ax_top.set_xticks(x + bar_width * (len(unique_algorithms) - 1) / 2)
ax_bottom.set_xticklabels(('Most Used', 'Most Reliable', 'Most Unreliable', 'Most Used x10'), rotation=0, ha='center')
# ~ ax2.set_xticklabels(('Most Used', 'Most Reliable', 'Most Unreliable', 'Most Used x10'), rotation=0, ha='center')
ax_bottom.set_ylim(0, 100)
ax_top.set_ylim(0, 100)
ax_top.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)
ax_bottom.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)
# Add legends
# Combine handles for the legend and place them outside the plot for clarity
handles, labels = plt.gca().get_legend_handles_labels()
fig.legend([handles[idx] for idx in order], [labels[idx] for idx in order], loc='lower center', bbox_to_anchor=(0.54, -0.12), fancybox=False, ncol=4)

plt.tight_layout()

plt.savefig(f"plot/combined/nodes_evolution_storage_only_{folder_suffix1}_{folder_suffix2}.pdf")
