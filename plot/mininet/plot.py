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

def create_folder(folder_path):
    try:
        # Create the folder if it does not exist
        os.makedirs(folder_path, exist_ok=True)
        print(f"Folder '{folder_path}' is ready.")
    except Exception as e:
        print(f"An error occurred: {e}")

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

folder_path = "plot/" + mode + "/" + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + "_" + str(number_of_loops)
create_folder(folder_path)

if mode != "mininet" and mode != "drex_only":
    print("mode must be drex_only or mininet")

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
    
    # ~ shutil.copy("output_alg1_stats.csv", folder_path + "/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "/alg1.csv")
    # ~ shutil.copy("output_alg4_stats.csv", folder_path + "/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "/drex.csv")
    # ~ shutil.copy("output_glusterfs_6_4_stats.csv", folder_path + "/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "/glusterfs_6_4.csv")
    # ~ shutil.copy("output_hdfsrs_3_2_stats.csv", folder_path + "output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "/hdfsrs_3_2.csv")
    # ~ shutil.copy("output_hdfsrs_6_3_stats.csv", folder_path + "/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "/hdfsrs_6_3.csv")
    # ~ shutil.copy("output_hdfs_three_replications_stats.csv", folder_path + "/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "/hdfs_three_replications.csv")
    # ~ shutil.copy("output_random_stats.csv", folder_path + "/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "/random.csv")
    
    # Load the data from the CSV file
    file_path1 = folder_path + "/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "_" + str(number_of_loops) + ".csv"

df1 = pd.read_csv(file_path1, quotechar='"', doublequote=True, skipinitialspace=True)

# Rename algorithms
df1['algorithm'] = df1['algorithm'].str.replace('_reduced_complexity', '_rc')
df1['algorithm'] = df1['algorithm'].str.replace('alg1', 'Min_Storage')
df1['algorithm'] = df1['algorithm'].str.replace('alg4', 'D-rex')
df1['algorithm'] = df1['algorithm'].str.replace('hdfs_three_replications', '3_replications')
df1['algorithm'] = df1['algorithm'].str.replace('hdfs_3_replication_c', 'hdfs_3_replications')
df1['algorithm'] = df1['algorithm'].str.replace('hdfsrs_3_2', 'HDFS_RS(3,2)')
df1['algorithm'] = df1['algorithm'].str.replace('hdfsrs_6_3', 'HDFS_RS(6,3)')
df1['algorithm'] = df1['algorithm'].str.replace('glusterfs_6_4', 'GlusterFS')
df1['algorithm'] = df1['algorithm'].str.replace('Min_Storage_c', 'Min_Storage')
df1['algorithm'] = df1['algorithm'].str.replace('alg_bogdan', 'Greedy_Load_Balancing')
df1['algorithm'] = df1['algorithm'].str.replace('glusterfs_6_4_c', 'GlusterFS')
df1['algorithm'] = df1['algorithm'].str.replace('GlusterFS_c', 'GlusterFS')
df1['algorithm'] = df1['algorithm'].str.replace('hdfs_rs_3_2_c', 'HDFS_RS(3,2)')
df1['algorithm'] = df1['algorithm'].str.replace('hdfs_rs_6_3_c', 'HDFS_RS(6,3)')
df1['algorithm'] = df1['algorithm'].str.replace('random_c', 'Random')

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
    'HDFS_RS(6,3)': 'red',
    'RS(10,4)': 'red',
    'vandermonders_3_2': 'red',
    'vandermonders_6_3': 'red',
    'vandermonders_10_4': 'red',
    'GlusterFS': 'red'
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

# Plotting mean chunking time
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['mean_chunking_time'] + df1['mean_parralelized_upload_time'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Mean Upload + Replication Time')
plt.title('Mean Upload + Replication Time (s)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(folder_path + '/mean_chunking_and_parallel_upload_time' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

# Plotting mean chunking time + paralel
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

# Unparalelized upload time
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['total_upload_time'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Upload Time')
plt.title('Total Upload Time (s or ms for mininet)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig(folder_path + '/total_upload_time_non_parallelized_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")

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
# ~ print("n algo:", num_algorithms)
# Initialize lists to store the values
initial_node_sizes_values = []
final_node_sizes_values = []

# Iterate over each row in the DataFrame
for index, row in df1.iterrows():
    # ~ print(row)
    # ~ print(row['initial_node_sizes'])
    # Convert the string representation of the list to an actual list for both columns
    initial_node_sizes_list = ast.literal_eval(row['initial_node_sizes'])
    final_node_sizes_list = ast.literal_eval(row['final_node_sizes'])
    
    # Append the lists to the respective lists
    initial_node_sizes_values.append(initial_node_sizes_list)
    final_node_sizes_values.append(final_node_sizes_list)
    
# ~ print(initial_node_sizes_values)
num_nodes=len(initial_node_sizes_list)
number_of_algorithms = len(initial_node_sizes_values)
# ~ print("There are", num_nodes, "nodes and", number_of_algorithms, "algorithms")

# Plot bars
df = None
value1 = []
value2 = []
categories = []
algs = []
# ~ print(num_nodes, "nodes")
categories = [f'HDD-{i+1}' for i in range(num_nodes)]
# ~ print(categories)

for a, limit in enumerate(zip(initial_node_sizes_values, final_node_sizes_values)):
    line_initial = limit[0]
    line_final = limit[1]
    for value_initial, value_final in zip(line_initial, line_final):
        value1.append(value_initial/1000000)
        value2.append((value_initial - value_final)/1000000)
        algs.append(a)

df = pd.DataFrame({'Category': categories*(number_of_algorithms), 'Value1': value1, 'Value2': value2, 'Algorithm': algs})

# ~ df_1 = df.loc[df['Algorithm'] == 0].reset_index()
# ~ df_2 = df.loc[df['Algorithm'] == 1].reset_index()
# Create a list to store DataFrames for each algorithm
dfs = []
# Loop through each algorithm and create filtered DataFrames
for alg in range(number_of_algorithms):
    df_filtered = df.loc[df['Algorithm'] == alg].reset_index()
    dfs.append(df_filtered)
    
# ~ df = df_1.merge(df_2, left_on='Category', right_on='Category', suffixes=['_0', '_1'])
# Start with the first DataFrame
merged_df = dfs[0]
print(len(dfs))
# Merge all DataFrames based on 'Category'
for i in range(1, len(dfs)):
    print("i =", i)
    merged_df = merged_df.merge(dfs[i], left_on='Category', right_on='Category', suffixes=[f'_{i-1}', f'_{i}'])
    # ~ print(dfs[i])

merged_df.rename(columns={
    'Value1': f'Value1_{number_of_algorithms-1}',
    'Value2': f'Value2_{number_of_algorithms-1}',
    'Algorithm': f'Algorithm_{number_of_algorithms-1}'
}, inplace=True)

# ~ print(merged_df)
# Change font of plot to Times
plt.rcParams.update({
    # ~ "text.usetex": True,
    # ~ "font.family": 'Times New Roman',
    # ~ "font.family": 'times',
    "xtick.color": 'grey',
    "ytick.color": 'grey'
})

# Initialize the matplotlib figure
# ~ algos = [0, 1
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
    ax.set_ylabel('Size (TB)')

    # Remove top and right border
    ax.spines[['right', 'top']].set_visible(False)

    # Configure legend
    v1 = Patch(facecolor='#1a80bb', label='Storage space')
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
