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
    total_possible_size_to_store = 487000*250
elif folder_suffix == "_FB_merged_365_-1.0_1_max0":
    total_possible_size_to_store = 928000000*1
else:
    print("Error suffix", folder_suffix, "not known")
    exit(1)

# Nice figs
plt.style.use("/home/gonthier/Chicago/paper.mplstyle")
pt = 1./72.27
jour_sizes = {"PRD": {"onecol": 246.*pt, "twocol": 510.*pt},
              "CQG": {"onecol": 374.*pt},}
my_width = jour_sizes["PRD"]["twocol"]
golden = (1 + 5 ** 0.5) / 2

base_dir = 'plot/drex_only'
set_of_node_regex = re.compile(r'^(.+)' + re.escape(folder_suffix) + r'$')

# Combined plot for 'size_stored' as bars and 'efficiency' as hashed bars
metric_to_plot_bars = 'size_stored'
metric_to_plot_efficiency = 'efficiency'


colors = ['#1f77b4', '#ffbf00', '#17becf', '#2ca02c', '#800000', '#d62728', '#ff7f0e', '#7f7f7f']
order = [0, 2, 1, 3, 4, 5, 7, 6]  # The new order for labels (C first, A second, B third)

# ~ plt.figure(figsize=(my_width, my_width/golden))

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
# ~ print(set_of_nodes)
# Convert the data into a DataFrame
df_data = pd.DataFrame(data, columns=['Set of Nodes', 'Algorithm', 'size_stored', 'efficiency'])

# Rename algorithms
df_data['Algorithm'] = df_data['Algorithm'].str.replace('alg1_c', 'GreedyMinStorage')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('alg4_1', 'D-Rex SC')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_3_replication_c', 'HDFS 3 Rep')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfsrs_3_2', 'HDFS(3,2)')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfsrs_6_3', 'HDFS(6,3)')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('glusterfs_6_4', 'GlusterFS')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('Min_Storage_c', 'Min_Storage')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('alg_bogdan', 'D-Rex LB')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('glusterfs_6_4_c', 'GlusterFS')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('glusterfs_0_0_c', 'GlusterFS_ADAPTATIVE')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('GlusterFS_c', 'GlusterFS')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_3_2_c', 'HDFS(3,2)')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_6_3_c', 'HDFS(6,3)')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_4_2_c', 'HDFS(4,2)')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_0_0_c', 'HDFS_RS_ADAPTATIVE')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('random_c', 'Random')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('daos_1_0_c', 'DAOS')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('daos_2_0_c', 'DAOS_2R')
    
# Filter out rows where the value is 0 in the column you want to plot
df_data = df_data[(df_data['size_stored'] != 0) & (df_data['efficiency'] != 0)]

# Filter out some algorithm
algorithms_to_exclude = ['HDFS(4,2)', 'GlusterFS_ADAPTATIVE', 'DAOS_2R', 'HDFS_RS_ADAPTATIVE']
filtered_df = df_data[~df_data['Algorithm'].isin(algorithms_to_exclude)]
        
# Initialize the figure and axes
fig, ax1 = plt.subplots(figsize=(my_width, my_width/golden))

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
# ~ print(set_of_nodes)
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
    ax1.bar(x + i * bar_width, [storage_data[set_of_node][i] for set_of_node in sets_of_nodes], width=bar_width, alpha=1, lw=1, label=f'{scheduler}', edgecolor='black', color=colors[i])

# Create a second y-axis for efficiency (hashed bars)
ax2 = ax1.twinx()

# Plot efficiency as hashed bars (with different hatches) on the left y-axis
for i, scheduler in enumerate(unique_algorithms):
    ax2.bar(x + i * bar_width, [efficiency_data[set_of_node][i] for set_of_node in sets_of_nodes], width=bar_width, alpha=0.4, hatch='xx', label=f'Efficiency ({scheduler})', edgecolor='black', lw=1, color=colors[i])

ax1.set_ylim(0,100)
ax2.set_ylim(0,14)

# Set labels
# ~ ax1.set_xlabel('Set of Nodes')
ax1.set_ylabel('Proportion of Data Sizes Stored (\%) (bar)')
ax2.set_ylabel('Efficiency (hashed bar)')

# Adding x-ticks
ax1.set_xticks(x + bar_width * (len(unique_algorithms) - 1) / 2)
ax1.set_xticklabels(('Most Used', 'Most Reliable', 'Most Unreliable', 'Most Used x10'), rotation=0, ha='center')

# Draw thinner vertical lines behind the bars
for tick in x[1:]:  # Start from the second x-tick
    ax1.axvline(x=tick - 2*bar_width, color='black', linestyle='-', linewidth=0.5, zorder=1)

# Adding a legend
handles, labels = ax1.get_legend_handles_labels()
ax1.legend([handles[idx] for idx in order], [labels[idx] for idx in order], loc='upper center', bbox_to_anchor=(0.5, -0.11), fancybox=False, ncol=4)

# Add a grid behind the bars for better readability
ax1.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)



# Save the plot
folder_path = "plot/combined/nodes_evolution" + folder_suffix
# ~ create_folder(folder_path)
plt.tight_layout()
plt.savefig(folder_path + '.pdf')
