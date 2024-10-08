# python3 plot_evolution_of_chunk_and_reconstruct_times.py

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
            # ~ print(reliability_threshold)
            # ~ print(index)
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
                    
                    # Fetch the algorithm names and corresponding values
                    for i, algorithm in enumerate(df['algorithm']):
                        value1 = df['total_parralelized_upload_time'].iloc[i]
                        value2 = df['total_chunking_time'].iloc[i]
                        value3 = df['total_read_time_parrallelized'].iloc[i]
                        value4 = df['total_reconstruct_time'].iloc[i]
                        data.append((reliability_threshold, algorithm, value1, value2, value3, value4))

# Convert the data into a DataFrame
df_data = pd.DataFrame(data, columns=['Reliability Threshold', 'Algorithm', 'total_parralelized_upload_time', 'total_chunking_time', 'total_read_time_parrallelized', 'total_reconstruct_time'])

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
df_data = df_data[(df_data['total_parralelized_upload_time'] != 0) & (df_data['total_read_time_parrallelized'] != 0) & (df_data['total_chunking_time'] != 0) & (df_data['total_reconstruct_time'] != 0)]

# List of algorithms to filter out
algorithms_to_exclude = ['HDFS_RS(3,2)', 'HDFS_RS(6,3)', 'GlusterFS', 'GlusterFS_c', 'DAOS_1R']
filtered_df = df_data[~df_data['Algorithm'].isin(algorithms_to_exclude)]

# Initialize the figure and axes
fig, ax1 = plt.subplots(figsize=(10, 6))

# Set bar width and positions
bar_width = 0.11

# Initialize dictionaries for efficiency and storage data
total_parralelized_upload_time_data = {}
total_chunking_time_data = {}
total_read_time_parrallelized_data = {}
total_reconstruct_time_data = {}

# Group the DataFrame by 'Reliability Threshold'
grouped = filtered_df.groupby('Reliability Threshold')

# Get all unique algorithms
unique_algorithms = filtered_df['Algorithm'].unique()

# Iterate over each group
for threshold, group in grouped:
    # Initialize lists with NaN for each algorithm
    total_parralelized_upload_time_list = [np.nan] * len(unique_algorithms)
    total_chunking_time_list = [np.nan] * len(unique_algorithms)
    total_read_time_parrallelized_list = [np.nan] * len(unique_algorithms)
    total_reconstruct_time_list = [np.nan] * len(unique_algorithms)
    
    # Map algorithm names to their respective index
    algorithm_index = {alg: index for index, alg in enumerate(unique_algorithms)}
    
    # Sort the group by Algorithm to ensure consistent order
    sorted_group = group.sort_values(by='Algorithm')
    
    # Populate the lists with efficiencies and sizes stored
    for _, row in group.iterrows():
        index = algorithm_index[row['Algorithm']]
        total_parralelized_upload_time_list[index] = row['total_parralelized_upload_time']
        total_chunking_time_list[index] = row['total_chunking_time']
        total_read_time_parrallelized_list[index] = row['total_read_time_parrallelized']
        total_reconstruct_time_list[index] = row['total_reconstruct_time']

    # Insert lists into the dictionaries with the reliability threshold as the key
    total_parralelized_upload_time_data[threshold] = total_parralelized_upload_time_list
    total_chunking_time_data[threshold] = total_chunking_time_list
    total_read_time_parrallelized_data[threshold] = total_read_time_parrallelized_list
    total_reconstruct_time_data[threshold] = total_reconstruct_time_list
    
# Extract unique schedulers (algorithms)
schedulers = filtered_df['Algorithm'].unique().tolist()
reliability_thresholds = sorted(filtered_df['Reliability Threshold'].unique().tolist())

# Display the organized data
x = np.arange(len(reliability_thresholds))  # x positions for reliability thresholds
# ~ print("Efficiency Data:", efficiency_data)
# ~ print("Storage Data:", storage_data)
# ~ print("Storage Data:", storage_data)
# ~ print("reliability_thresholds:", reliability_thresholds)
# ~ print("schedulers:", schedulers)

# plot stacked bars
hatches = ['/', '\\', '|', '-']  # Feel free to customize hatches
colors = ['blue', 'green', 'red', 'orange', 'gray', 'pink', 'yellow', 'purple']  # One color for each scheduler
for i, scheduler in enumerate(schedulers):
    # Get the data for total_parralelized_upload_time
    total_upload_data = [total_parralelized_upload_time_data[threshold][i] for threshold in reliability_thresholds]
    chunking_time_data = [total_chunking_time_data[threshold][i] for threshold in reliability_thresholds]
    total_read_data = [total_read_time_parrallelized_data[threshold][i] for threshold in reliability_thresholds]
    reconstruct_time_data = [total_reconstruct_time_data[threshold][i] for threshold in reliability_thresholds]
    bottom = [0] * len(reliability_thresholds)  # Reset bottom for stacking

    # First stack total_parralelized_upload_time bars
    bars1 = ax1.bar(x + i * bar_width, total_upload_data, width=bar_width, bottom=bottom, alpha=0.6, 
                    label=f'total_parralelized_upload_time ({scheduler})', edgecolor='black', hatch=hatches[0], color=colors[i])
    # Update bottom for the next data set
    bottom = [b + t for b, t in zip(bottom, total_upload_data)]
    
    # Stack chunking_time_data on top of total_upload_data
    bars2 = ax1.bar(x + i * bar_width, chunking_time_data, width=bar_width, bottom=bottom, alpha=0.6, 
                    label=f'chunking_time ({scheduler})', edgecolor='black', hatch=hatches[1], color=colors[i])
    # Update bottom for any further stacking
    bottom = [b + c for b, c in zip(bottom, chunking_time_data)]
    
    # Stack total_read_data
    bars3 = ax1.bar(x + i * bar_width, total_read_data, width=bar_width, bottom=bottom, alpha=0.6, 
                    label=f'total_read_data ({scheduler})', edgecolor='black', hatch=hatches[2], color=colors[i])
    # Update bottom for any further stacking
    bottom = [b + d for b, d in zip(bottom, total_read_data)]
    
    # Stack reconstruct_time_data
    bars4 = ax1.bar(x + i * bar_width, reconstruct_time_data, width=bar_width, bottom=bottom, alpha=0.6, 
                    label=f'reconstruct_time_data ({scheduler})', edgecolor='black', hatch=hatches[3], color=colors[i])
    # Update bottom for any further stacking
    bottom = [b + e for b, e in zip(bottom, reconstruct_time_data)]
    
    
    
# ~ # Plot total storage as bars
# ~ for i, scheduler in enumerate(schedulers):
    # ~ bars = ax1.bar(x + i * bar_width, [total_parralelized_upload_time_data[threshold][i] for threshold in reliability_thresholds], width=bar_width, alpha=0.6, label=f'total_parralelized_upload_time ({scheduler})', edgecolor='black')

# Set labels
ax1.set_xlabel('Minimum Reliability Requirement')
ax1.set_ylabel('total_parralelized_upload_time')

# Adding x-ticks
ax1.set_xticks(x + bar_width * (len(unique_algorithms) - 1) / 2)
ax1.set_xticklabels(reliability_thresholds)

line_colors = []
for i, scheduler in enumerate(schedulers):
    line_color = f"C{i}"  # Get the color used for the line
    line_colors.append(line_color)  # Store color for legend

# Custom legend
handles = []
for i, scheduler in enumerate(schedulers):
    # Create a bar handle for storage
    bar_handle = plt.Line2D([0], [0], color=line_colors[i], lw=4, label=f'{scheduler}')
    handles.append(bar_handle)

# Combine handles into a single legend
ax1.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4)  # Adjusted the legend position

# Add a grid behind the bars for better readability
ax1.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)  # Added a grid behind bars

# Save the plot
plt.tight_layout()
plt.savefig("plot/combined/" + folder_prefix + "total_times" + folder_suffix + ".pdf")
