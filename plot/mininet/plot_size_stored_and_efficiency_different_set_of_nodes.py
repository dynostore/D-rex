import os
import pandas as pd
import matplotlib.pyplot as plt
import csv
import re
import sys
import numpy as np
from matplotlib.ticker import LogLocator
from functools import partial

def create_folder(folder_path):
    try:
        os.makedirs(folder_path, exist_ok=True)
    except Exception as e:
        print(f"An error occurred: {e}")

# Prompt the user for the folder suffix
folder_suffix = sys.argv[1]  # This will be the part of the folder name after the set of nodes

if folder_suffix == "_MEVA_merged_365_-1.0_25_max0":
    total_possible_size_to_store = 487000*25
elif folder_suffix == "_MEVA_merged_365_-1.0_250_max0":
    total_possible_size_to_store *= 487000*250
else:
    print("Error suffix", folder_suffix, "not known")
    exit(1)

base_dir = 'plot/drex_only'
set_of_node_regex = re.compile(r'^(.+)' + re.escape(folder_suffix) + r'$')

# Combined plot for 'size_stored' as bars and 'efficiency' as hashed bars
metric_to_plot_bars = 'size_stored'
metric_to_plot_efficiency = 'efficiency'

plt.figure(figsize=(10, 6))

data = []
df_data = []
df = []

# Traverse through each folder
for folder in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder)
    if os.path.isdir(folder_path):
        match = set_of_node_regex.search(folder)
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
                    df = pd.read_csv(file_path, quotechar='"', doublequote=True, skipinitialspace=True)
                    
                    # Calculate efficiency
                    df['efficiency'] = df['size_stored'] / (df['total_parralelized_upload_time'] + df['total_chunking_time'] + df['total_read_time_parrallelized'] + df['total_reconstruct_time'])
                    
                    # Fetch the algorithm names and corresponding values
                    for i, algorithm in enumerate(df['algorithm']):
                        size_stored_value = (df[metric_to_plot_bars].iloc[i] * 100) / total_possible_size_to_store
                        efficiency_value = df[metric_to_plot_efficiency].iloc[i]
                        data.append((set_of_nodes, algorithm, size_stored_value, efficiency_value))

# Convert the data into a DataFrame
df_data = pd.DataFrame(data, columns=['Set of Nodes', 'Algorithm', 'size_stored', 'efficiency'])

# Rename algorithms as per previous logic
df_data['Algorithm'] = df_data['Algorithm'].replace({
    'alg1': 'Min_Storage',
    'alg4_1': 'D-rex',
    'hdfs_3_replication_c': 'hdfs_3_replications',
    'hdfsrs_3_2': 'HDFS_RS(3,2)',
    'hdfsrs_6_3': 'HDFS_RS(6,3)',
    'glusterfs_6_4': 'GlusterFS',
    'Min_Storage_c': 'Min_Storage',
    'alg_bogdan': 'Greedy_Load_Balancing',
    'glusterfs_0_0_c': 'GlusterFS_ADAPTATIVE',
    'hdfs_rs_3_2_c': 'HDFS_RS(3,2)',
    'hdfs_rs_6_3_c': 'HDFS_RS(6,3)',
    'hdfs_rs_4_2_c': 'HDFS_RS(4,2)',
    'hdfs_rs_0_0_c': 'HDFS_RS_ADAPTATIVE',
    'random_c': 'Random',
    'daos_1_0_c': 'DAOS_1R',
    'daos_2_0_c': 'DAOS_2R'
})

# Filter out rows where the value is 0 in the column you want to plot
df_data = df_data[(df_data['size_stored'] != 0) & (df_data['efficiency'] != 0)]

# List of algorithms to filter out
algorithms_to_exclude = ['HDFS_RS(3,2)', 'HDFS_RS(6,3)', 'GlusterFS', 'GlusterFS_c', 'DAOS_1R']
filtered_df = df_data[~df_data['Algorithm'].isin(algorithms_to_exclude)]

# Initialize the figure and axes
fig, ax1 = plt.subplots(figsize=(12, 6))

# Set bar width and positions with more space between sets of nodes
bar_width = 0.09
bar_spacing = 0.3  # Adjust spacing between sets of nodes

# Initialize dictionaries for efficiency and storage data
efficiency_data = {}
storage_data = {}

# Group the DataFrame by 'Set of Nodes'
grouped = filtered_df.groupby('Set of Nodes')

# Get all unique algorithms
unique_algorithms = filtered_df['Algorithm'].unique()

# Iterate over each group
for set_of_nodes, group in grouped:
    # Initialize lists with NaN for each algorithm
    efficiency_list = [np.nan] * len(unique_algorithms)
    storage_list = [np.nan] * len(unique_algorithms)
    
    # Map algorithm names to their respective index
    algorithm_index = {alg: index for index, alg in enumerate(unique_algorithms)}
    
    # Populate the lists with efficiencies and sizes stored
    for _, row in group.iterrows():
        index = algorithm_index[row['Algorithm']]
        efficiency_list[index] = row['efficiency']
        storage_list[index] = row['size_stored']

    # Insert lists into the dictionaries with the set of nodes as the key
    efficiency_data[set_of_nodes] = efficiency_list
    storage_data[set_of_nodes] = storage_list

# Extract unique sets of nodes
sets_of_nodes = filtered_df['Set of Nodes'].unique().tolist()

# Set positions on the x-axis with more spacing between node sets
x = np.arange(len(sets_of_nodes)) * (len(unique_algorithms) * bar_width + bar_spacing)  # Adjusted for more spacing

# Plot total storage as bars
for i, scheduler in enumerate(unique_algorithms):
    ax1.bar(x + i * bar_width, [storage_data[set_of_nodes][i] for set_of_nodes in sets_of_nodes], 
            width=bar_width, alpha=0.6, label=f'Storage Used ({scheduler})', edgecolor='black')

# Plot efficiency as hashed bars (with different hatches) on the left y-axis
for i, scheduler in enumerate(unique_algorithms):
    ax1.bar(x + i * bar_width, [efficiency_data[set_of_nodes][i] for set_of_nodes in sets_of_nodes], 
            width=bar_width, alpha=0.4, hatch='//', label=f'Efficiency ({scheduler})', edgecolor='black')

# Set labels
ax1.set_xlabel('Set of Nodes')
ax1.set_ylabel('Proportion of Data Sizes Stored (%) & Efficiency (hashed bars)')

# Adding x-ticks
ax1.set_xticks(x + bar_width * (len(unique_algorithms) - 1) / 2)
ax1.set_xticklabels(sets_of_nodes)

# Custom legend
handles = []
for i, scheduler in enumerate(unique_algorithms):
    # Create a bar handle for storage
    bar_handle = plt.Line2D([0], [0], color=f"C{i}", lw=4, label=f'{scheduler}')
    handles.append(bar_handle)

# Combine handles into a single legend
ax1.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4)

# Add a grid behind the bars for better readability
ax1.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)



# Save the plot
folder_path = "plot/combined/nodes_evolution" + folder_suffix
# ~ create_folder(folder_path)
plt.tight_layout()
plt.savefig(folder_path + '.pdf')
