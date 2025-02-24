
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
folder_suffix = sys.argv[1]  # This will be the part of the folder name after the set of nodes
mode = sys.argv[2]

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
# ~ golden = (1 + 5 ** 0.5) / 1.5 # Smaller height
golden = (1 + 5 ** 0.5) / 2.4 # Higher height
plt.rcParams.update({
    'axes.labelsize': 14,       # Axis label font size
    'legend.fontsize': 14,      # Legend font size
    'xtick.labelsize': 14,      # X-axis tick label font size
})

base_dir = 'plot/drex_only'
set_of_node_regex = re.compile(r'^(.+)' + re.escape(folder_suffix) + r'$')

# Combined plot for 'size_stored' as bars and 'throughput' (renamed from efficiency) as hashed bars
metric_to_plot_bars = 'size_stored'
metric_to_plot_efficiency = 'efficiency'

colors = ['#1f77b4', '#17becf','#ffbf00', '#7f7f7f', '#800000', '#d62728', '#ff7f0e', '#2ca02c']
# ~ colors = ['#1f77b4', '#ffbf00', '#17becf', '#800000', '#d62728', '#ff7f0e', '#7f7f7f']
order = [0, 2, 1, 3, 4, 6, 7]  # The new order for labels (C first, A second, B third)
# ~ order = [0, 2, 1, 7, 6, 3, 4, 5]

data = []
df_data = []
df = []
throughput_optimal_all = []
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
                throughput_optimal = 0
                for row in csv_reader:
                    number_of_data_stored_optimal = int(row[0])
                    total_storage_used_optimal = float(row[1])
                    best_upload_time_optimal = float(row[2])
                    best_read_time_optimal = float(row[3])
                    size_stored_optimal = float(row[4])
                    
                    throughput_optimal += size_stored_optimal / (best_upload_time_optimal + best_read_time_optimal)
                print("throughput_optimal:", throughput_optimal)
                throughput_optimal_all.append(throughput_optimal)
                
            # Read all CSV files in the folder
            for file in os.listdir(folder_path):
                if file.endswith('.csv') and file.startswith('output_drex_only'):
                    file_path = os.path.join(folder_path, file)
                    df = pd.read_csv(file_path, quotechar='"', doublequote=True, skipinitialspace=True)
                    
                    # Calculate throughput (renamed from efficiency)
                    df['throughput'] = df['size_stored'] / (df['total_parralelized_upload_time'] + df['total_chunking_time'] + df['total_read_time_parrallelized'] + df['total_reconstruct_time'])
                    
                    # Fetch the algorithm names and corresponding values
                    for i, algorithm in enumerate(df['algorithm']):
                        size_stored_value = (df[metric_to_plot_bars].iloc[i] * 100) / total_possible_size_to_store
                        throughput_value = df['throughput'].iloc[i]
                        data.append((set_of_nodes, algorithm, size_stored_value, throughput_value))

# Convert the data into a DataFrame
df_data = pd.DataFrame(data, columns=['Set of Nodes', 'Algorithm', 'size_stored', 'throughput'])

# Rename algorithms
df_data['Algorithm'] = df_data['Algorithm'].replace({
    'alg1_c': 'GreedyMinStorage', 'alg4_1': 'D-Rex SC',
    'hdfs_3_replication_c': '3 Replication', 'hdfsrs_3_2': 'EC(3,2)',
    'hdfsrs_6_3': 'EC(6,3)', 'glusterfs_6_4': 'EC(4,2)',
    'Min_Storage_c': 'Min_Storage', 'alg_bogdan': 'D-Rex LB',
    'glusterfs_6_4_c': 'EC(4,2)', 'glusterfs_0_0_c': 'EC(4,2)',
    'GlusterFS_c': 'EC(4,2)', 'hdfs_rs_3_2_c': 'EC(3,2)',
    'hdfs_rs_6_3_c': 'EC(6,3)', 'hdfs_rs_4_2_c': 'HDFS(4,2)',
    'hdfs_rs_0_0_c': 'HDFS_RS_ADAPTATIVE', 'random_c': 'Random',
    'daos_1_0_c': 'DAOS', 'daos_2_0_c': 'DAOS_2R', 'least_used_node': 'GreedyLeastUsed'
})

# Filter out rows where the value is 0 in the column you want to plot
df_data = df_data[(df_data['size_stored'] != 0) & (df_data['throughput'] != 0)]

# Filter out some algorithms
algorithms_to_exclude = ['HDFS(4,2)', 'GlusterFS_ADAPTATIVE', 'DAOS_2R', 'HDFS_RS_ADAPTATIVE', '3 Replication']
filtered_df = df_data[~df_data['Algorithm'].isin(algorithms_to_exclude)]

# ~ fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(my_width, my_width/(golden)), sharex=True, gridspec_kw={'height_ratios': [1, 1]})

bar_width = 0.09
bar_spacing = 0.3  # Adjust spacing between sets of nodes

# Initialize dictionaries for throughput and storage data
throughput_data = {}
storage_data = {}

# Group the DataFrame by 'Set of Nodes'
grouped = filtered_df.groupby('Set of Nodes')

# Get all unique algorithms
unique_algorithms = filtered_df['Algorithm'].unique()

# Iterate over each group
for set_of_nodes, group in grouped:
    efficiency_list = [np.nan] * len(unique_algorithms)
    storage_list = [np.nan] * len(unique_algorithms)
    
    algorithm_index = {alg: index for index, alg in enumerate(unique_algorithms)}
    
    for _, row in group.iterrows():
        index = algorithm_index[row['Algorithm']]
        storage_list[index] = row['size_stored']
        efficiency_list[index] = row['throughput']
    
    throughput_data[set_of_nodes] = efficiency_list
    storage_data[set_of_nodes] = storage_list
    print(efficiency_list)
    print(storage_list)

sets_of_nodes = filtered_df['Set of Nodes'].unique().tolist()
x = np.arange(len(sets_of_nodes)) * (len(unique_algorithms) * bar_width + bar_spacing)


if mode != "all":
    # Only plot storage when mode is 'all'
    golden = (1 + 5 ** 0.5) / 2.2
    fig, ax = plt.subplots(figsize=(my_width, my_width / golden))

    bar_width = 0.09
    bar_spacing = 0.3

    sets_of_nodes = filtered_df['Set of Nodes'].unique().tolist()
    x = np.arange(len(sets_of_nodes)) * (len(unique_algorithms) * bar_width + bar_spacing)

    # Plot storage data
    for i, scheduler in enumerate(unique_algorithms):
        ax.bar(x + i * bar_width, [storage_data[set_of_node][i] for set_of_node in sets_of_nodes],
               width=bar_width, alpha=0.6, label=f'{scheduler}', color=colors[i], edgecolor='black')

    ax.set_ylabel('Proportion of Data Sizes Stored (\%)')
    ax.set_xticks(x + bar_width * (len(unique_algorithms) - 1) / 2)
    ax.set_xticklabels(('Most Used', 'Most Reliable', 'Most Unreliable', 'Homogeneous'), rotation=0, ha='center')
    ax.set_ylim(0, 100)
    ax.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)

    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.5, -0.41), fancybox=False, ncol=3)

    plt.tight_layout()
    plt.savefig("plot/combined/nodes_evolution_storage" + folder_suffix + ".pdf")

else:
    # Plot both throughput and storage
    fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(my_width, my_width / golden), sharex=True,
                                             gridspec_kw={'height_ratios': [1, 1]})
    x = np.arange(len(sets_of_nodes)) * (len(unique_algorithms) * bar_width + bar_spacing)

    # Plot throughput data on top
    for i, scheduler in enumerate(unique_algorithms):
        ax_top.bar(x + i * bar_width, [throughput_data[set_of_node][i] for set_of_node in sets_of_nodes],
                   width=bar_width, alpha=0.6, label=f'{scheduler}', color=colors[i], edgecolor='black', hatch='//')

    # Plot optimal throughput lines
    for i, set_of_node in enumerate(sets_of_nodes):
        ax_top.hlines(y=throughput_optimal_all[i], xmin=x[i] - bar_width / 2,
                      xmax=x[i] + (len(unique_algorithms) - 0.5) * bar_width,
                      color='blue', linewidth=2, linestyle='--', label='Ideal Throughput' if i == 0 else None)

    # Plot storage data on bottom
    for i, scheduler in enumerate(unique_algorithms):
        ax_bottom.bar(x + i * bar_width, [storage_data[set_of_node][i] for set_of_node in sets_of_nodes],
                      width=bar_width, alpha=0.6, label=f'{scheduler}', color=colors[i], edgecolor='black')

    # Set labels and formatting
    ax_top.set_ylabel('Throughput (MB/s)')
    ax_bottom.set_ylabel('Proportion of Data Sizes Stored (\%)')
    ax_bottom.set_xticks(x + bar_width * (len(unique_algorithms) - 1) / 2)
    ax_bottom.set_xticklabels(('Most Used', 'Most Reliable', 'Most Unreliable', 'Homogeneous'), rotation=0, ha='center')

    ax_top.set_ylim(0, 15)
    ax_bottom.set_ylim(0, 100)
    ax_top.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)
    ax_bottom.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)

    # Add legend
    handles, labels = ax_top.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', bbox_to_anchor=(0.54, -0.18), fancybox=False, ncol=3)

    plt.tight_layout()
    plt.savefig("plot/combined/nodes_evolution_throughput_and_storage" + folder_suffix + ".pdf")





# ~ # Plot efficiency data on the top subplot
# ~ for i, scheduler in enumerate(unique_algorithms):
    # ~ bars = ax_top.bar(x + i * bar_width, [throughput_data[set_of_node][i] for set_of_node in sets_of_nodes], 
                      # ~ width=bar_width, alpha=0.6, label=f'{scheduler}', color=colors[i], edgecolor='black', hatch='//')

# ~ legend_handles = []

# ~ for i, set_of_node in enumerate(sets_of_nodes):
    # ~ optimal_throughput = throughput_optimal_all[i]  # Use index since throughput_optimal_all is a list
    # ~ oracle_line = ax_top.hlines(
        # ~ y=optimal_throughput, 
        # ~ xmin=x[i] - bar_width / 2,  # Start slightly before the first bar
        # ~ xmax=x[i] + (len(unique_algorithms) - 0.5) * bar_width,  # End slightly after the last bar
        # ~ color='blue', 
        # ~ linewidth=2, 
        # ~ linestyle='--', 
        # ~ label='Ideal Throughput' if i == 0 else None  # Add legend only once
    # ~ )
    # ~ if i == 0:  # Add the first "Oracle" line to the legend
        # ~ legend_handles.append(oracle_line)

    
# ~ # Plot storage data on the bottom subplot
# ~ for i, scheduler in enumerate(unique_algorithms):
    # ~ print(i, scheduler)
    # ~ bars = ax_bottom.bar(x + i * bar_width, [storage_data[set_of_node][i] for set_of_node in sets_of_nodes], 
                         # ~ width=bar_width, alpha=0.6, label=f'{scheduler}', color=colors[i], edgecolor='black')
    # ~ legend_handles.append(bars)

# ~ # Set labels and limits
# ~ ax_bottom.set_ylabel('Proportion of Data Sizes Stored (\%)')
# ~ ax_top.set_ylabel('Throughput (MB/s)')
# ~ ax_bottom.set_xticks(x + bar_width * (len(unique_algorithms) - 1) / 2)
# ~ ax_top.set_xticks(x + bar_width * (len(unique_algorithms) - 1) / 2)
# ~ ax_bottom.set_xticklabels(('Most Used', 'Most Reliable', 'Most Unreliable', 'Homogeneous'), rotation=0, ha='center')
# ~ ax_bottom.set_ylim(0, 100)
# ~ ax_top.set_ylim(0, 15)
# ~ ax_top.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)
# ~ ax_bottom.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)

# ~ # Create custom handles for ax1 without hatching
# ~ handles, labels = plt.gca().get_legend_handles_labels()
# ~ fig.legend(legend_handles, [h.get_label() for h in legend_handles], loc='lower center', bbox_to_anchor=(0.54, -0.18), fancybox=False, ncol=3)
# ~ plt.tight_layout()

# ~ # Save the figures as PDFs
# ~ plt.savefig("plot/combined/nodes_evolution_throughput_and_storage" + folder_suffix + ".pdf")
