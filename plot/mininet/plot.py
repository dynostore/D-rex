# python3 plot/plot.py ${data_duration_on_system} ${reliability_threshold} number_input_data data_size
#   
# python3 plot/mininet/plot.py 10 1 mininet
# python3 plot/mininet/plot.py 1 10 mininet
# python3 plot/mininet/plot.py 1 100 mininet
# python3 plot/mininet/plot.py 10 200 mininet
# python3 plot/mininet/plot.py 10 100 mininet

import pandas as pd
import matplotlib as mpl
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import sys
import shutil
import os
import ast
import csv
import seaborn as sns
import numpy as np

def move_file_if_exists(src, dest):
    if os.path.exists(src):
        shutil.move(src, dest)
    else:
        raise FileNotFoundError(f"File {src} does not exist.")
        
def create_folder(folder_path):
    try:
        # Create the folder if it does not exist
        os.makedirs(folder_path, exist_ok=True)
        print(f"Folder '{folder_path}' is ready.")
    except Exception as e:
        print(f"An error occurred: {e}")

# Function to calculate slowdowns for a given scheduler
def calculate_slowdown(scheduler_df, optimal_df):
    # ~ scheduler_df['slowdown_transfer'] = (scheduler_df['Transfer_Time_Parralelized'] + scheduler_df['Chunking_Time']) / (optimal_df['Transfer_Time_Parralelized'] + optimal_df['Chunking_Time'])
    # ~ scheduler_df['slowdown_read'] = (scheduler_df['Read_Time_Parralelized'] + scheduler_df['Reconstruct_Time']) / (optimal_df['Read_Time_Parralelized'] + optimal_df['Reconstruct_Time'])
    scheduler_df['slowdown_transfer'] = (scheduler_df['Transfer_Time_Parralelized'] + scheduler_df['Chunking_Time'])
    scheduler_df['slowdown_read'] = (scheduler_df['Read_Time_Parralelized'] + scheduler_df['Reconstruct_Time'])
    
    return scheduler_df

def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def count_lines_minus_one(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        return len(lines) - 1

data_duration_on_system = int(sys.argv[1])
reliability_threshold = float(sys.argv[2])
mode = sys.argv[3] # mininet or drex_only
plot_type = sys.argv[4] # 'combined' or 'individual'
input_nodes = sys.argv[5]
if is_int(sys.argv[6]):
    number_input_data = int(sys.argv[6])
    data_size = int(sys.argv[7])
    input_data_to_print = str(number_input_data) + "_" + str(data_size)
else:
    input_data = sys.argv[6]
    number_of_loops = int(sys.argv[7])
    max_N = int(sys.argv[8])
    node_removal = int(sys.argv[9])
    input_data_to_print = input_data.split('/')[-1]
    input_data_to_print = input_data_to_print.rsplit('.', 1)[0]
    # ~ number_input_data = count_lines_minus_one(input_data)
    number_input_data = 0
    with open(input_data, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Check if the 'Access Type' column has the value '2'
            if row['Access Type'] == '2':
                number_input_data += 1
    number_input_data = number_input_data*number_of_loops
print(number_input_data, "input data")

input_nodes_to_print = input_nodes.split('/')[-1]
input_nodes_to_print = input_nodes_to_print.rsplit('.', 1)[0]

if node_removal != 0:
    folder_path = "plot/" + mode + "/" + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + "_" + str(number_of_loops) + "_max" + str(max_N) + "_node_removal"
else:
    folder_path = "plot/" + mode + "/" + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + "_" + str(number_of_loops) + "_max" + str(max_N)
create_folder(folder_path)

if mode != "mininet" and mode != "drex_only":
    print("mode must be drex_only or mininet")

files_to_move = [
    ("output_alg1_c_stats.csv", folder_path + "/alg1_c.csv"),
    ("output_alg4_1_stats.csv", folder_path + "/alg4_1.csv"),
    ("output_alg_bogdan_stats.csv", folder_path + "/alg_bogdan.csv"),
    ("output_daos_1_0_c_stats.csv", folder_path + "/daos_1_0_c.csv"),
    ("output_daos_2_0_c_stats.csv", folder_path + "/daos_2_0_c.csv"),
    ("output_glusterfs_0_0_c_stats.csv", folder_path + "/glusterfs_0_0_c.csv"),
    ("output_glusterfs_6_4_c_stats.csv", folder_path + "/gluster_fs_6_4_c.csv"),
    ("output_hdfs_3_replication_c_stats.csv", folder_path + "/hdfs_3_replication_c.csv"),
    ("output_hdfs_rs_0_0_c_stats.csv", folder_path + "/hdfs_rs_0_0_c.csv"),
    ("output_hdfs_rs_3_2_c_stats.csv", folder_path + "/hdfs_rs_3_2_c.csv"),
    ("output_hdfs_rs_4_2_c_stats.csv", folder_path + "/hdfs_rs_4_2_c.csv"),
    ("output_hdfs_rs_6_3_c_stats.csv", folder_path + "/hdfs_rs_6_3_c.csv"),
    ("output_optimal_schedule.csv", folder_path + "/output_optimal_schedule.csv"),
    ("output_optimal_schedule_stats.csv", folder_path + "/optimal_schedule.csv"),
    ("output_random_c_stats.csv", folder_path + "/random_c.csv"),
    ("output_least_used_node_stats.csv", folder_path + "/least_used_node.csv")
]

if mode == "mininet":
    # Copy csv files
    shutil.copy("../D-Rex-Simulation-experiments/src/outputtimes.csv", "plot/mininet/data/outputtimes_" + input_nodes_to_print + "_" + input_data_to_print + ".csv")
    shutil.copy("../D-Rex-Simulation-experiments/src/outputfiles.csv", "plot/mininet/data/outputfiles_" + input_nodes_to_print + "_" + input_data_to_print + ".csv")

    # Load the data from the CSV files
    file_path1 = "plot/mininet/data/outputtimes_" + input_nodes_to_print + "_" + input_data_to_print + ".csv"
    file_path2 = "plot/mininet/data/outputfiles_" + input_nodes_to_print + "_" + input_data_to_print + ".csv"
    
    df2 = pd.read_csv(file_path2)
    df2['algorithm'] = df2['algorithm'].str.replace('_reduced_complexity', '_rc')
else:
    # Copy csv file
    shutil.copy("output_drex_only.csv", folder_path + "/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "_" + str(number_of_loops) + ".csv")
    
    for src, dest in files_to_move:
        try:
            move_file_if_exists(src, dest)
        except FileNotFoundError as e:
            print(e)  # Continue to the next file
        
    # Load the data from the CSV file
    file_path1 = folder_path + "/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "_" + str(number_of_loops) + ".csv"

print("Read", file_path1)
df1 = pd.read_csv(file_path1, quotechar='"', doublequote=True, skipinitialspace=True)

# Rename algorithms
df1['algorithm'] = df1['algorithm'].str.replace('_reduced_complexity', '_rc')
df1['algorithm'] = df1['algorithm'].str.replace('alg1', 'Min_Storage')
df1['algorithm'] = df1['algorithm'].str.replace('D-rex_1', 'D-rex')
df1['algorithm'] = df1['algorithm'].str.replace('hdfs_three_replications', '3_replications')
df1['algorithm'] = df1['algorithm'].str.replace('hdfs_3_replication_c', 'hdfs_3_replications')
df1['algorithm'] = df1['algorithm'].str.replace('hdfsrs_3_2', 'HDFS_RS(3,2)')
df1['algorithm'] = df1['algorithm'].str.replace('hdfsrs_6_3', 'HDFS_RS(6,3)')
df1['algorithm'] = df1['algorithm'].str.replace('glusterfs_6_4', 'GlusterFS')
df1['algorithm'] = df1['algorithm'].str.replace('Min_Storage_c', 'Min_Storage')
df1['algorithm'] = df1['algorithm'].str.replace('alg_bogdan', 'Greedy_Load_Balancing')
df1['algorithm'] = df1['algorithm'].str.replace('glusterfs_6_4_c', 'GlusterFS')
df1['algorithm'] = df1['algorithm'].str.replace('glusterfs_0_0_c', 'GlusterFS_ADAPTATIVE')
df1['algorithm'] = df1['algorithm'].str.replace('GlusterFS_c', 'GlusterFS')
df1['algorithm'] = df1['algorithm'].str.replace('hdfs_rs_3_2_c', 'HDFS_RS(3,2)')
df1['algorithm'] = df1['algorithm'].str.replace('hdfs_rs_6_3_c', 'HDFS_RS(6,3)')
df1['algorithm'] = df1['algorithm'].str.replace('hdfs_rs_4_2_c', 'HDFS_RS(4,2)')
df1['algorithm'] = df1['algorithm'].str.replace('hdfs_rs_0_0_c', 'HDFS_RS_ADAPTATIVE')
df1['algorithm'] = df1['algorithm'].str.replace('random_c', 'Random')
df1['algorithm'] = df1['algorithm'].str.replace('daos_1_0_c', 'DAOS_1R')
df1['algorithm'] = df1['algorithm'].str.replace('daos_2_0_c', 'DAOS_2R')
df1['algorithm'] = df1['algorithm'].str.replace('least_used_node', 'GreedyLeastUsed')

# Define colors
colors = {
    'Min_Storage': 'green',
    'Min_Time': 'green',
    'alg3': 'blue',
    'D-rex': 'blue',
    'random': 'green',
    'Random': 'green',
    'hdfs': 'green',
    '3_replications': 'red',
    'hdfs_3_replications': 'red',
    'Greedy_Load_Balancing': 'green',
    'alg2_rc': 'blue',
    'alg3_rc': 'blue',
    'alg4_rc': 'blue',
    'HDFS_RS(3,2)': 'red',
    'HDFS_RS(4,2)': 'red',
    'HDFS_RS(6,3)': 'red',
    'RS(10,4)': 'red',
    'vandermonders_3_2': 'red',
    'vandermonders_6_3': 'red',
    'vandermonders_10_4': 'red',
    'GlusterFS': 'red',
    'GreedyLeastUsed': 'green'
}

# Function to get colors based on algorithm names
def get_colors(algorithms):
    return [colors.get(alg, 'gray') for alg in algorithms]

# Plots unique to mininet
if mode == "mininet":
    # Plotting total_simulation_time
    plt.figure(figsize=(10, 6))
    plt.bar(df1['algorithm'], df1['total_simulation_time'], color=get_colors(df1['algorithm']))
    plt.xlabel('Algorithm')
    plt.ylabel('Total Simulation Time')
    plt.title('Total Simulation Time (ms)')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(folder_path + '/total_simulation_time_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

    # Plotting total_chunking_time
    plt.figure(figsize=(10, 6))
    plt.bar(df1['algorithm'], df1['total_chunking_time'], color=get_colors(df1['algorithm']))
    print(df1['total_chunking_time'])
    plt.xlabel('Algorithm')
    plt.ylabel('Total Chunk Time')
    plt.title('Total Chunk Time (ms)')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(folder_path + '/total_chunk_time_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")
    
    # Plotting total_parralelized_upload_time
    plt.figure(figsize=(10, 6))
    plt.bar(df1['algorithm'], df1['total_upload_time'], color=get_colors(df1['algorithm']))
    plt.xlabel('Algorithm')
    plt.ylabel('Total Parralelized Upload Time')
    plt.title('Total Parralelized Upload Time (ms)')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(folder_path + '/total_parralelized_upload_time_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")
    
    # ~ # Unparalelized upload time
    # ~ plt.figure(figsize=(10, 6))
    # ~ plt.bar(df1['algorithm'], df1['total_upload_times_non_parallelized'], color=get_colors(df1['algorithm']))
    # ~ plt.xlabel('Algorithm')
    # ~ plt.ylabel('Total Upload Time')
    # ~ plt.title('Total Upload Time (ms)')
    # ~ plt.xticks(rotation=90)
    # ~ plt.tight_layout()
    # ~ plt.savefig(folder_path + '/total_upload_time_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")
else: # Plots unique to drex_only
    # Plotting number_of_data_stored
    plt.figure(figsize=(10, 6))
    plt.bar(df1['algorithm'], df1['number_of_data_stored'], color=get_colors(df1['algorithm']))
    plt.xlabel('Algorithm')
    plt.axhline(y=number_input_data, color='black', linestyle='dotted')
    plt.ylabel('Number of data stored')
    plt.title('Number of data stored')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(folder_path + '/number_of_data_stored_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

    # Plotting mean number of chunks
    plt.figure(figsize=(10, 6))
    plt.bar(df1['algorithm'], df1['mean_N'], color=get_colors(df1['algorithm']))
    plt.xlabel('Algorithm')
    plt.ylabel('Number of chunks per data')
    plt.title('Number of chunks per data')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(folder_path + '/number_of_chunks_per_data_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

    # Plotting mean_storage_used
    plt.figure(figsize=(10, 6))
    plt.bar(df1['algorithm'], df1['mean_storage_used'], color=get_colors(df1['algorithm']))
    plt.xlabel('Algorithm')
    plt.ylabel('Storage per data (MB)')
    plt.title('Storage per data')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(folder_path + '/storage_per_data_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")
    
    # Plotting mean_upload_time
    plt.figure(figsize=(10, 6))
    plt.bar(df1['algorithm'], df1['mean_upload_time'], color=get_colors(df1['algorithm']))
    plt.xlabel('Algorithm')
    plt.ylabel('Upload time non parallel per data (s)')
    plt.title('Upload time non parallel per data')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(folder_path + '/mean_upload_time_non_parallelized' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")
    
    # Plotting mean_parralelized_upload_time
    plt.figure(figsize=(10, 6))
    plt.bar(df1['algorithm'], df1['mean_parralelized_upload_time'], color=get_colors(df1['algorithm']))
    plt.xlabel('Algorithm')
    plt.ylabel('Upload time parralelized per data (s)')
    plt.title('Upload time parralelized per data')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(folder_path + '/mean_parralelized_upload_time' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")


# Plot for both mininet and drex_only
# Plotting total_storage_used
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['total_storage_used'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Storage Used')
plt.title('Total Storage Used (MB)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(folder_path + '/total_storage_used_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

# Plotting total chunking time
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['total_chunking_time'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Chunking Time')
plt.title('Total Chunking Time (s)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(folder_path + '/total_chunking_time' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

# Plotting mean chunking time + paralel
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['mean_chunking_time'] + df1['mean_parralelized_upload_time'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Mean Upload + Replication Time')
plt.title('Mean Upload + Replication Time (s)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(folder_path + '/mean_chunking_and_parallel_upload_time' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

# Plotting mean read time + mean reconstruct
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['mean_read_time_parrallelized'] + df1['mean_reconstruct_time'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Mean Read + Reconstruct Time')
plt.title('Mean Read + Reconstruct Time (s)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(folder_path + '/mean_reconstruct_and_parallel_read_time' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

# Plotting mean chunking time
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['mean_chunking_time'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Mean Chunking Time')
plt.title('Mean Chunking Time (s)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(folder_path + '/mean_chunking_time' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

# Plotting total_scheduling_time
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['total_scheduling_time'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Scheduling Time')
plt.title('Total Scheduling Time (ms for minient, s for drex_only)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(folder_path + '/total_scheduling_time_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

# Plotting size_stored
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['size_stored'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('size_stored')
plt.title('size_stored (MB)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(folder_path + '/size_stored_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

# Unparalelized upload time
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['total_upload_time'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Upload Time')
plt.title('Total Upload Time (s or ms for mininet)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(folder_path + '/total_upload_time_non_parallelized_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

# Unparalelized read time
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['total_read_time'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Read Time')
plt.title('Total Read Time (s or ms for mininet)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(folder_path + '/total_read_time_non_parallelized_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

# parallel read time
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['total_read_time_parrallelized'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Read Time parrallelized')
plt.title('Total Read Time parrallelized (s or ms for mininet)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(folder_path + '/total_read_time_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

# Plotting total_parralelized_upload_time
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['total_parralelized_upload_time'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Parralelized Upload Time')
plt.title('Total Parralelized Upload Time (s or ms for mininet)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(folder_path + '/total_parralelized_upload_time' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")


# Plot for distribution of data on the different storage nodes
# Number of algorithms and storage nodes
num_algorithms = len(df1)
# Calculate bar width and positions
bar_width = 0.2
# Initialize lists to store the values
initial_node_sizes_values = []
final_node_sizes_values = []

# Iterate over each row in the DataFrame
for index, row in df1.iterrows():
    # Convert the string representation of the list to an actual list for both columns
    initial_node_sizes_list = ast.literal_eval(row['initial_node_sizes'])
    final_node_sizes_list = ast.literal_eval(row['final_node_sizes'])
    
    # Append the lists to the respective lists
    initial_node_sizes_values.append(initial_node_sizes_list)
    final_node_sizes_values.append(final_node_sizes_list)
    
num_nodes=len(initial_node_sizes_list)
number_of_algorithms = len(initial_node_sizes_values)

# Plot bars
df = None
value1 = []
value2 = []
categories = []
algs = []
categories = [f'HDD-{i+1}' for i in range(num_nodes)]

for a, limit in enumerate(zip(initial_node_sizes_values, final_node_sizes_values)):
    line_initial = limit[0]
    line_final = limit[1]
    for value_initial, value_final in zip(line_initial, line_final):
        value1.append(value_initial/1000000)
        value2.append((value_initial - value_final)/1000000)
        algs.append(a)

df = pd.DataFrame({'Category': categories*(number_of_algorithms), 'Value1': value1, 'Value2': value2, 'Algorithm': algs})

# Create a list to store DataFrames for each algorithm
dfs = []
# Loop through each algorithm and create filtered DataFrames
for alg in range(number_of_algorithms):
    df_filtered = df.loc[df['Algorithm'] == alg].reset_index()
    dfs.append(df_filtered)
    
# Start with the first DataFrame
merged_df = dfs[0]
print(len(dfs))
# Merge all DataFrames based on 'Category'
for i in range(1, len(dfs)):
    merged_df = merged_df.merge(dfs[i], left_on='Category', right_on='Category', suffixes=[f'_{i-1}', f'_{i}'])
    
merged_df.rename(columns={
    'Value1': f'Value1_{number_of_algorithms-1}',
    'Value2': f'Value2_{number_of_algorithms-1}',
    'Algorithm': f'Algorithm_{number_of_algorithms-1}'
}, inplace=True)

# Change font of plot to Times
plt.rcParams.update({
    "xtick.color": 'grey',
    "ytick.color": 'grey'
})

# Initialize the matplotlib figure
algos = list(range(number_of_algorithms))
print(algos)

if plot_type == 'combined':
    fig, ax = plt.subplots()
    x0 = np.arange(len(categories))  # create an array of values for the ticks that can perform arithmetic with width (w)
    x0 = x0 * 2.5

    # build the plots
    stacks = len(algos)  # how many stacks in each group for a tick location
    values = ['Value1', 'Value2']
    colors = ['#1a80bb', '#ea801c']
    hatches = [None, '//']
    # set the width
    w = 1

    # this needs to be adjusted based on the number of stacks; each location needs to be split into the proper number of locations
    x1 = list(zip(list(x0 - w/stacks), list(x0 + w/stacks)))

    for i, row in df.iterrows():
        for a in algos:
            bottom = 0
            for c_idx, v in enumerate(values):
                height = row[f'{v}_{a}']
                bc = ax.bar(x=x1[i][a], height=height, width=w, bottom=bottom, edgecolor='black', color=colors[c_idx], linewidth='1', hatch=hatches[a])
                bc[0]._hatch_color = mpl.colors.to_rgba("darkgrey")
                bc[0].stale = True
                # ~ bottom += height
            
    ax.set_xticks(x0)
    _ = ax.set_xticklabels(categories)
    ax.set_xlabel('Category')
    ax.set_ylabel('Storage Size (TB)')

    # Remove top and right border
    ax.spines[['right', 'top']].set_visible(False)

    # Configure legend
    v1 = Patch(facecolor='#1a80bb', label='Total storage space')
    v2 = Patch(facecolor='#ea801c', label='Used storage')
    a1 = Patch(facecolor='white', edgecolor='black', label='Algorithm 1') 
    a2 = Patch(facecolor='white', edgecolor='black', hatch='////', label='Algorithm 2') 
    a2._hatch_color = mpl.colors.to_rgba("darkgrey")
    a2.stale = True

    # Adding legend
    plt.legend(handles=[v1, v2, a1, a2])
    # Display the plot
    plt.savefig(folder_path + '/storage_distribution_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")
else:
    for a in algos:
        plt.figure(figsize=(8, 4))
        # Plot the first set of bars
        sns.barplot(
            x='Category',
            y=f'Value1_{a}',
            # ~ data=df,
            data=merged_df,
            color='#1a80bb',
            edgecolor='black',
            linewidth=1.5,
            label='Storage space'
        )

        # Plot the second set of bars on top of the first set
        sns.barplot(
            x='Category',
            y=f'Value2_{a}',
            # ~ data=df,
            data=merged_df,
            color='#ea801c',
            bottom=0,
            edgecolor='black',
            linewidth=1.5,
            label='Used storage'
        )

        plt.ylabel('Size (TB)')
        plt.xlabel(str(df1['algorithm'][a]))
        plt.legend()
        print(str(df1['algorithm'][a]))
        plt.savefig(folder_path + '/storage_distribution_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + "_" + str(df1['algorithm'][a]) + ".pdf")


# Plot relative to optimal
# Initialize variables to store the data
number_of_data_stored_optimal = 0
total_storage_used_optimal = 0
best_upload_time_optimal = 0
best_read_time_optimal = 0

# Read the CSV file
with open(folder_path + "/output_optimal_schedule.csv", mode='r') as file:
    csv_reader = csv.reader(file)
    
    # Skip the header
    next(csv_reader)
    
    # Read the single row of values
    for row in csv_reader:
        number_of_data_stored_optimal = int(row[0])
        total_storage_used_optimal = float(row[1])
        best_upload_time_optimal = float(row[2])
        best_read_time_optimal = float(row[3])
        size_stored_optimal = float(row[4])

# Print the values (optional)
print(f"Size stored optimal: {size_stored_optimal}")
print(df1['size_stored'])
print(f"Total storage used: {total_storage_used_optimal}")
print(f"Best upload time: {best_upload_time_optimal}")
print(df1['total_parralelized_upload_time'] + df1['total_chunking_time'])
print(f"Best read time: {best_read_time_optimal}")
print(df1['total_read_time_parrallelized'] + df1['total_reconstruct_time'])

# Best fit score
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], best_upload_time_optimal/(df1['total_parralelized_upload_time'] + df1['total_chunking_time']) + best_read_time_optimal/(df1['total_read_time_parrallelized'] + df1['total_reconstruct_time']) + df1['size_stored']/size_stored_optimal, color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Best Fit')
plt.title('Best Fit')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(folder_path + '/best_fit_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

# Efficiency
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['size_stored']/(df1['total_parralelized_upload_time'] + df1['total_chunking_time'] + df1['total_read_time_parrallelized'] + df1['total_reconstruct_time']), color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Efficiency')
plt.title('Efficiency')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(folder_path + '/efficiency_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")







## Violin plots
# Load the optimal schedule if the threshold is -1
# ~ if reliability_threshold == -1:
if 1 == 1:
    optimal_df = pd.read_csv(folder_path + "/optimal_schedule.csv")

    # List of CSV files to read
    scheduler_files = [
        folder_path + "/alg4_1.csv", folder_path + "/alg1_c.csv",
        folder_path + "/alg_bogdan.csv", folder_path + "/daos_1_0_c.csv",
        folder_path + "/daos_2_0_c.csv", folder_path + "/gluster_fs_6_4_c.csv",
        folder_path + "/glusterfs_0_0_c.csv", folder_path + "/hdfs_3_replication_c.csv",
        folder_path + "/hdfs_rs_0_0_c.csv", folder_path + "/hdfs_rs_3_2_c.csv",
        folder_path + "/hdfs_rs_4_2_c.csv", folder_path + "/hdfs_rs_6_3_c.csv", folder_path + "/least_used_node.csv"
    ]

    # Dictionary to store data for plotting
    slowdown_data = {'scheduler': [], 'slowdown_type': [], 'slowdown_value': []}

    # Process each scheduler file from the predefined list
    for scheduler_file in scheduler_files:
        scheduler_name = os.path.basename(scheduler_file).split('.')[0]  # Extract scheduler name from filename
        
        # Read the CSV file
        try:
            scheduler_df = pd.read_csv(scheduler_file)
        except FileNotFoundError:
            print(f"File {scheduler_file} not found.")
            continue
        
        # Skip the file if it's empty (only header is present)
        if scheduler_df.empty:
            print(f"Skipping {scheduler_file}, no data found.")
            continue
        
        # Calculate the slowdown
        scheduler_df = calculate_slowdown(scheduler_df, optimal_df)
        
        # Append data for Transfer and Chunking slowdown
        slowdown_data['scheduler'].extend([scheduler_name] * len(scheduler_df) * 2)  # Repeat for both types
        slowdown_data['slowdown_type'].extend(['Transfer + Chunking'] * len(scheduler_df) + ['Read + Reconstruct'] * len(scheduler_df))
        slowdown_data['slowdown_value'].extend(scheduler_df['slowdown_transfer'].values)
        slowdown_data['slowdown_value'].extend(scheduler_df['slowdown_read'].values)

    # Convert slowdown data to a DataFrame
    slowdown_df = pd.DataFrame(slowdown_data)

    # Create a violin plot with split violins for each scheduler
    plt.figure(figsize=(20, 8))
    sns.violinplot(
        x='scheduler', y='slowdown_value', hue='slowdown_type',
        data=slowdown_df, split=True, inner="quartile"
    )

    plt.title('Slowdown Comparison: Transfer + Chunking vs Read + Reconstruct')
    plt.xlabel('Scheduler')
    plt.ylabel('Slowdown Value')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.ylim(0, 10)  # Set y-axis limits from 0 to 10
    
    # Save the plot
    plt.savefig(folder_path + '/violin_plot_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")
