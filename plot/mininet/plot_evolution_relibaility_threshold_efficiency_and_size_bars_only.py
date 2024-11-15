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

def count_decimal_places(value):
    value_str = str(value)
    if '.' in value_str:
        return len(value_str.split('.')[1])
    else:
        return 0

# Nice figs
plt.style.use("/home/gonthier/Chicago/paper.mplstyle")
pt = 1./72.27
jour_sizes = {"PRD": {"onecol": 246.*pt, "twocol": 510.*pt},
              "CQG": {"onecol": 374.*pt},
              "PRDFULLPAGE": {"twocol": 1000.*pt},}
my_width = jour_sizes["PRDFULLPAGE"]["twocol"]
golden = (1 + 5 ** 0.5) / 2
golden = (1 + 5 ** 0.5) / 1.5 # Smaller height
plt.rcParams.update({
    'axes.labelsize': 14,       # Axis label font size
    'legend.fontsize': 14,      # Legend font size
    'xtick.labelsize': 14,      # X-axis tick label font size
})

# Prompt the user for folder name parts before and after the reliability threshold
folder_prefix = sys.argv[1]
folder_suffix = sys.argv[2]

if folder_prefix == "10_most_used_nodes_MEVA_merged_365_" or folder_prefix == "10_most_unreliable_nodes_MEVA_merged_365_":
    total_possible_size_to_store = 487000
else: 
    print("Folder prefix not known") 
    exit
if folder_suffix == "_250_max0":
    total_possible_size_to_store = total_possible_size_to_store*250
elif folder_suffix == "_25_max0":
    total_possible_size_to_store = total_possible_size_to_store*25
else:
    print("Folder sufix not known") 
    exit
    
base_dir = 'plot/drex_only'
threshold_regex = re.compile(re.escape(folder_prefix) + r'(\d+\.\d+)' + re.escape(folder_suffix) + r'$')
markers = ['o', 's', 'D', '^', 'v', '>', '<', 'p', 'h', '*', 'x', '+', '|', '_', '.', ',', '1', '2', '3', '4']

# Combined plot for 'size_stored' as bars and 'efficiency' as lines
metric_to_plot_bars = 'size_stored'
metric_to_plot_lines = 'efficiency'

index = 0
data = []
df_data = []
df = []

# Traverse through each folder
for folder in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder)
    if os.path.isdir(folder_path):
        match = threshold_regex.search(folder)
        if match:
            print(folder_path)
            reliability_threshold = float(match.group(1))
            index = count_decimal_places(reliability_threshold)
            print(reliability_threshold)
            print(index)
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
                        size_stored_value = (df[metric_to_plot_bars].iloc[i]*100)/total_possible_size_to_store
                        efficiency_value = df[metric_to_plot_lines].iloc[i]
                        data.append((reliability_threshold, algorithm, size_stored_value, efficiency_value))

# Convert the data into a DataFrame
df_data = pd.DataFrame(data, columns=['Reliability Threshold', 'Algorithm', 'size_stored', 'efficiency'])

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
df_data['Algorithm'] = df_data['Algorithm'].str.replace('GlusterFS_c', 'EC(4,2)')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_3_2_c', 'EC(3,2)')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_6_3_c', 'EC(6,3)')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_4_2_c', 'HDFS(4,2)')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_0_0_c', 'HDFS_RS_ADAPTATIVE')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('random_c', 'Random')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('daos_1_0_c', 'DAOS')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('daos_2_0_c', 'DAOS_2R')

# Filter out rows where the value is 0 in the column you want to plot
df_data = df_data[(df_data['size_stored'] != 0) & (df_data['efficiency'] != 0)]

# List of algorithms to filter out
algorithms_to_exclude = ['HDFS(4,2)', 'GlusterFS_ADAPTATIVE', 'DAOS_2R', 'HDFS_RS_ADAPTATIVE']
filtered_df = df_data[~df_data['Algorithm'].isin(algorithms_to_exclude)]

# Set bar width and positions
bar_width = 0.09
# Initialize dictionaries for efficiency and storage data
efficiency_data = {}
storage_data = {}

# Group the DataFrame by 'Reliability Threshold'
grouped = filtered_df.groupby('Reliability Threshold')

# Get all unique algorithms
unique_algorithms = filtered_df['Algorithm'].unique()
# Iterate over each group
for threshold, group in grouped:
    # Initialize lists with NaN for each algorithm
    efficiency_list = [np.nan] * len(unique_algorithms)
    storage_list = [np.nan] * len(unique_algorithms)
    # Map algorithm names to their respective index
    algorithm_index = {alg: index for index, alg in enumerate(unique_algorithms)}
    
    # Sort the group by Algorithm to ensure consistent order
    sorted_group = group.sort_values(by='Algorithm')
    
    # Populate the lists with efficiencies and sizes stored
    for _, row in group.iterrows():
        index = algorithm_index[row['Algorithm']]
        efficiency_list[index] = row['efficiency']
        storage_list[index] = row['size_stored']

    # Insert lists into the dictionaries with the reliability threshold as the key
    efficiency_data[threshold] = efficiency_list
    storage_data[threshold] = storage_list
    
# Extract unique schedulers (algorithms)
schedulers = filtered_df['Algorithm'].unique().tolist()
reliability_thresholds = sorted(filtered_df['Reliability Threshold'].unique().tolist())
# Display the organized data
x = np.arange(len(reliability_thresholds))  # x positions for reliability thresholds
print("Efficiency Data:", efficiency_data)
print("Storage Data:", storage_data)
print("Storage Data:", storage_data)
print("reliability_thresholds:", reliability_thresholds)
print("schedulers:", schedulers)

# Initialize the figure and two subplots sharing the same x-axis
fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(my_width, my_width/(golden)), sharex=True, gridspec_kw={'height_ratios': [1, 1]})
bar_width = 0.09

# Colors, markers, and order to maintain color consistency across both subplots
colors = ['#1f77b4', '#ffbf00', '#17becf', '#2ca02c', '#800000', '#d62728', '#ff7f0e', '#7f7f7f']
order = [0, 2, 1, 3, 4, 5, 7, 6]

# Plot efficiency data on the top subplot
for i, scheduler in enumerate(schedulers):
    bars = ax_top.bar(x + i * bar_width, [efficiency_data[threshold][i] for threshold in reliability_thresholds], 
                      width=bar_width, alpha=0.6, label=f'{scheduler}', color=colors[i], edgecolor='black', hatch='//')
ax_top.set_ylabel('Throughput (MB/s)')
ax_top.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)


# optimal line
# ~ mean_optimal_throughput = size_stored_optimal/(best_upload_time_optimal + best_read_time_optimal)
# ~ ax_top.axhline(mean_optimal_throughput, color='blue', linestyle='--', linewidth=1.5, label='Mean optimal throughput')

# Plot storage data on the bottom subplot
for i, scheduler in enumerate(schedulers):
    bars = ax_bottom.bar(x + i * bar_width, [storage_data[threshold][i] for threshold in reliability_thresholds], 
                         width=bar_width, alpha=0.6, label=f'{scheduler}', color=colors[i], edgecolor='black')
ax_bottom.set_ylim(0, 100)
ax_bottom.set_ylabel('Proportion of Data Sizes Stored (\%)')
ax_bottom.set_xlabel('Minimum Reliability Requirement')
ax_bottom.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)

# Adding x-ticks and setting tick labels
ax_bottom.set_xticks(x + bar_width * (len(unique_algorithms) - 1) / 2)
# ~ ax_bottom.set_xticklabels(reliability_thresholds)
# Custom ticks
# ~ tick_positions = [0.9, 0.99, 0.999, 0.9999, 0.99999, 0.999999, 0.9999999, 0.99999999, 0.999999999]
if folder_prefix == "10_most_unreliable_nodes_MEVA_merged_365_":
    tick_labels = [r'$1-10^{-1}$', r'$1-10^{-2}$', r'$1-10^{-3}$', r'$1-10^{-4}$', r'$1-10^{-5}$', r'$1-10^{-6}$', r'$1-10^{-7}$']
else:
    tick_labels = [r'$1-10^{-1}$', r'$1-10^{-2}$', r'$1-10^{-3}$', r'$1-10^{-4}$', r'$1-10^{-5}$', r'$1-10^{-6}$', r'$1-10^{-7}$', r'$1-10^{-8}$', r'$1-10^{-9}$']

# ~ ax_bottom.set_xticks(tick_positions)
ax_bottom.set_xticklabels(tick_labels)

# Combine handles for the legend and place them outside the plot for clarity
handles, labels = plt.gca().get_legend_handles_labels()
fig.legend([handles[idx] for idx in order], [labels[idx] for idx in order], loc='lower center', bbox_to_anchor=(0.5, -0.10), fancybox=False, ncol=4)

# Adjust layout for tight spacing
plt.tight_layout()

# Save the plot
plt.savefig(f"plot/combined/{folder_prefix}evolution{folder_suffix}.pdf")
