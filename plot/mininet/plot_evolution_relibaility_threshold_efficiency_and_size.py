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

# Prompt the user for folder name parts before and after the reliability threshold
folder_prefix = sys.argv[1]
folder_suffix = sys.argv[2]

if folder_prefix == "10_most_used_nodes_MEVA_merged_365_" or folder_prefix == "10_most_unreliable_nodes_MEVA_merged_365_":
    total_possible_size_to_store = 487000
if folder_suffix == "_250_max0":
    total_possible_size_to_store = total_possible_size_to_store*250
elif folder_suffix == "_25_max0":
    total_possible_size_to_store = total_possible_size_to_store*25

base_dir = 'plot/drex_only'
threshold_regex = re.compile(re.escape(folder_prefix) + r'(\d+\.\d+)' + re.escape(folder_suffix) + r'$')
markers = ['o', 's', 'D', '^', 'v', '>', '<', 'p', 'h', '*', 'x', '+', '|', '_', '.', ',', '1', '2', '3', '4']

# Combined plot for 'size_stored' as bars and 'efficiency' as lines
metric_to_plot_bars = 'size_stored'
metric_to_plot_lines = 'efficiency'

plt.figure(figsize=(10, 6))

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
                        # ~ size_stored_value = df[metric_to_plot_bars].iloc[i]
                        size_stored_value = (df[metric_to_plot_bars].iloc[i]*100)/total_possible_size_to_store
                        efficiency_value = df[metric_to_plot_lines].iloc[i]
                        data.append((reliability_threshold, algorithm, size_stored_value, efficiency_value))

# Convert the data into a DataFrame
df_data = pd.DataFrame(data, columns=['Reliability Threshold', 'Algorithm', 'size_stored', 'efficiency'])

# Rename algorithms
df_data['Algorithm'] = df_data['Algorithm'].str.replace('alg1', 'Min_Storage')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('alg4_1', 'D-rex')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_3_replication_c', 'hdfs_3_replications')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfsrs_3_2', 'HDFS_RS(3,2)')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfsrs_6_3', 'HDFS_RS(6,3)')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('glusterfs_6_4', 'GlusterFS')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('Min_Storage_c', 'Min_Storage')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('alg_bogdan', 'Greedy_Load_Balancing')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('glusterfs_6_4_c', 'GlusterFS')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('glusterfs_0_0_c', 'GlusterFS_ADAPTATIVE')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_3_2_c', 'HDFS_RS(3,2)')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_6_3_c', 'HDFS_RS(6,3)')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_4_2_c', 'HDFS_RS(4,2)')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_0_0_c', 'HDFS_RS_ADAPTATIVE')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('random_c', 'Random')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('daos_1_0_c', 'DAOS_1R')
df_data['Algorithm'] = df_data['Algorithm'].str.replace('daos_2_0_c', 'DAOS_2R')

# Filter out rows where the value is 0 in the column you want to plot
df_data = df_data[(df_data['size_stored'] != 0) & (df_data['efficiency'] != 0)]

# List of algorithms to filter out
algorithms_to_exclude = ['HDFS_RS(3,2)', 'HDFS_RS(6,3)', 'GlusterFS', 'GlusterFS_c', 'DAOS_1R']
filtered_df = df_data[~df_data['Algorithm'].isin(algorithms_to_exclude)]

# Initialize the figure and axes
fig, ax1 = plt.subplots(figsize=(10, 6))

# Set bar width and positions
bar_width = 0.11
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


# Plot total storage as bars
for i, scheduler in enumerate(schedulers):
    bars = ax1.bar(x + i * bar_width, [storage_data[threshold][i] for threshold in reliability_thresholds], 
                    width=bar_width, alpha=0.6, label=f'Storage Used ({scheduler})', edgecolor='black')

# Create a second y-axis for the efficiency lines
ax2 = ax1.twinx()
line_colors = []
for i, scheduler in enumerate(schedulers):
    line_color = f"C{i}"  # Get the color used for the line
    line_colors.append(line_color)  # Store color for legend
    # Plot the efficiency values for each scheduler at each reliability threshold
    ax2.plot(x + 3.4*bar_width, [efficiency_data[threshold][i] for threshold in reliability_thresholds],
             marker='o', color=line_color, label=f'Efficiency ({scheduler})')

# Set labels
ax1.set_xlabel('Minimum Reliability Requirement')
ax1.set_ylabel('Proportion of Data Sizes Stored (%) (bar)')
ax2.set_ylabel('Efficiency (line)')

# Adding x-ticks
ax1.set_xticks(x + bar_width * (len(unique_algorithms) - 1) / 2)
ax1.set_xticklabels(reliability_thresholds)

# Custom legend
handles = []
for i, scheduler in enumerate(schedulers):
    # Create a bar handle for storage
    bar_handle = plt.Line2D([0], [0], color=line_colors[i], lw=4, label=f'{scheduler}')
    handles.append(bar_handle)
    # ~ handles.append(dot_handle)

# ~ barr_handle = plt.Line2D([0], [0], color='grey', lw=4, label='Storage Used')
# ~ # Create a dot handle for efficiency
# ~ dot_handle = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='black', markersize=8,
                         # ~ label='Efficiency')
# ~ handles.append(barr_handle)
# ~ handles.append(dot_handle)

# Combine handles into a single legend
ax1.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4)  # Adjusted the legend position

# Add a grid behind the bars for better readability
ax1.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)  # Added a grid behind bars

# Save the plot
folder_path = "plot/drex_only/" + folder_prefix + "evolution" + folder_suffix
create_folder(folder_path)
plt.tight_layout()
plt.savefig(folder_path + '/size_stored_and_efficiency.pdf')
