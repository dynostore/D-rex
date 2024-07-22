# python3 plot/plot.py number_input_data data_size
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
import seaborn as sns
import numpy as np

number_input_data = int(sys.argv[1])
data_size = int(sys.argv[2])
mode = sys.argv[3] # mininet or drex_only
plot_type = sys.argv[4] # 'combined' or 'individual'

if mode != "mininet" and mode != "drex_only":
    print("mode must be drex_only or mininet")

if mode == "mininet":
    # Copy csv files
    shutil.copy("../D-Rex-Simulation-experiments/src/outputtimes.csv", "plot/mininet/data/outputtimes_" + str(number_input_data) + "_" + str(data_size) + "MB.csv")
    shutil.copy("../D-Rex-Simulation-experiments/src/outputfiles.csv", "plot/mininet/data/outputfiles_" + str(number_input_data) + "_" + str(data_size) + "MB.csv")

    # Load the data from the CSV files
    file_path1 = "plot/mininet/data/outputtimes_" + str(number_input_data) + "_" + str(data_size) + "MB.csv"
    file_path2 = "plot/mininet/data/outputfiles_" + str(number_input_data) + "_" + str(data_size) + "MB.csv"
    
    df2 = pd.read_csv(file_path2)
    df2['algorithm'] = df2['algorithm'].str.replace('_reduced_complexity', '_rc')
else:
    # ~ pass
    # ~ # Copy csv file
    shutil.copy("output_drex_only.csv", "plot/drex_only/data/output_drex_only_" + str(number_input_data) + "_" + str(data_size) + "MB.csv")
    
    # ~ # Load the data from the CSV file
    file_path1 = "plot/drex_only/data/output_drex_only_" + str(number_input_data) + "_" + str(data_size) + "MB.csv"

# ~ file_path1="output_drex_only_4_200000MB.csv"

df1 = pd.read_csv(file_path1, quotechar='"', doublequote=True, skipinitialspace=True)

# ~ # Rename algorithms
# ~ df1['algorithm'] = df1['algorithm'].str.replace('_reduced_complexity', '_rc')
# ~ df1['algorithm'] = df1['algorithm'].str.replace('alg1', 'Min Storage')
# ~ df1['algorithm'] = df1['algorithm'].str.replace('alg4', 'D-rex')
# ~ df1['algorithm'] = df1['algorithm'].str.replace('hdfs_three_replications', '3 replications')
# ~ df1['algorithm'] = df1['algorithm'].str.replace('hdfsrs_3_2', 'HDFS RS(3,2)')
# ~ df1['algorithm'] = df1['algorithm'].str.replace('hdfsrs_6_3', 'HDFS RS(6,3)')
# ~ df1['algorithm'] = df1['algorithm'].str.replace('glusterfs_6_4', 'GlusterFS')

# Define colors
colors = {
    'Min Storage': 'green',
    'Min Time': 'green',
    'alg3': 'blue',
    'D-rex': 'blue',
    'random': 'green',
    'hdfs': 'green',
    '3 replications': 'red',
    'alg2_rc': 'blue',
    'alg3_rc': 'blue',
    'alg4_rc': 'blue',
    'HDFS RS(3,2)': 'red',
    'HDFS RS(6,3)': 'red',
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
    plt.savefig('plot/' + mode + '/total_simulation_time_' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')

    # Plotting total_chunking_time
    plt.figure(figsize=(10, 6))
    plt.bar(df1['algorithm'], df1['total_chunking_time'], color=get_colors(df1['algorithm']))
    print(df1['total_chunking_time'])
    plt.xlabel('Algorithm')
    plt.ylabel('Total Chunk Time')
    plt.title('Total Chunk Time (ms)')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('plot/' + mode + '/total_chunk_time_' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')
    
    # Plotting total_parralelized_upload_time
    plt.figure(figsize=(10, 6))
    plt.bar(df1['algorithm'], df1['total_upload_time'], color=get_colors(df1['algorithm']))
    plt.xlabel('Algorithm')
    plt.ylabel('Total Parralelized Upload Time')
    plt.title('Total Parralelized Upload Time (ms)')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('plot/' + mode + '/total_parralelized_upload_time_' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')
    
    # Plotting total_parralelized_upload_time
    plt.figure(figsize=(10, 6))
    plt.bar(df1['algorithm'], df1['total_upload_times_non_parallelized'], color=get_colors(df1['algorithm']))
    plt.xlabel('Algorithm')
    plt.ylabel('Total Upload Time')
    plt.title('Total Upload Time (ms)')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('plot/' + mode + '/total_upload_time_' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')
else: # Plots unique to drex_only
    # ~ # Plotting total_parralelized_upload_time
    # ~ plt.figure(figsize=(10, 6))
    # ~ plt.bar(df1['algorithm'], df1['total_parralelized_upload_time'], color=get_colors(df1['algorithm']))
    # ~ plt.xlabel('Algorithm')
    # ~ plt.ylabel('Total Parralelized Upload Time')
    # ~ plt.title('Total Parralelized Upload Time (s)')
    # ~ plt.xticks(rotation=90)
    # ~ plt.tight_layout()
    # ~ plt.savefig('plot/' + mode + '/total_parralelized_upload_time' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')

    # ~ # Plotting total_upload_time
    # ~ plt.figure(figsize=(10, 6))
    # ~ plt.bar(df1['algorithm'], df1['total_upload_time'], color=get_colors(df1['algorithm']))
    # ~ plt.xlabel('Algorithm')
    # ~ plt.ylabel('Total Upload Time')
    # ~ plt.title('Total Upload Time (s)')
    # ~ plt.xticks(rotation=90)
    # ~ plt.tight_layout()
    # ~ plt.savefig('plot/' + mode + '/total_upload_time_' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')

    # Plotting number_of_data_stored
    plt.figure(figsize=(10, 6))
    plt.bar(df1['algorithm'], df1['number_of_data_stored'], color=get_colors(df1['algorithm']))
    plt.xlabel('Algorithm')
    plt.axhline(y=number_input_data, color='black', linestyle='dotted')
    plt.ylabel('Number of data stored')
    plt.title('Number of data stored')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('plot/' + mode + '/number_of_data_stored_' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')

    # Plotting mean number of chunks
    plt.figure(figsize=(10, 6))
    plt.bar(df1['algorithm'], df1['mean_N'], color=get_colors(df1['algorithm']))
    plt.xlabel('Algorithm')
    plt.ylabel('Number of chunks per data')
    plt.title('Number of chunks per data')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('plot/' + mode + '/number_of_chunks_per_data_' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')

    # Plotting mean_storage_used
    plt.figure(figsize=(10, 6))
    plt.bar(df1['algorithm'], df1['mean_storage_used'], color=get_colors(df1['algorithm']))
    plt.xlabel('Algorithm')
    plt.ylabel('Storage per data (MB)')
    plt.title('Storage per data')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('plot/' + mode + '/storage_per_data_' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')
    
    # Plotting mean_upload_time
    plt.figure(figsize=(10, 6))
    plt.bar(df1['algorithm'], df1['mean_upload_time'], color=get_colors(df1['algorithm']))
    plt.xlabel('Algorithm')
    plt.ylabel('Upload time per data (s)')
    plt.title('Upload time per data')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('plot/' + mode + '/mean_upload_time' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')


# Plot for both mininet and drex_only
# Plotting total_storage_used
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['total_storage_used'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Storage Used')
plt.title('Total Storage Used (MB)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('plot/' + mode + '/total_storage_used_' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')

# Plotting total_scheduling_time
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['total_scheduling_time'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Scheduling Time')
plt.title('Total Scheduling Time (ms for minient, s for drex_only)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('plot/' + mode + '/total_scheduling_time_' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')

# Plot for distribution of data on the different storage nodes
# Number of algorithms and storage nodes
num_algorithms = len(df1)
# ~ num_nodes = len(df1.loc[0, 'initial_node_sizes'])
# ~ num_nodes = 10
# Calculate bar width and positions
bar_width = 0.2
print("n algo:", num_algorithms)

# ~ num_nodes = 10 # A lire depuis le fichier ou ligne de commande plutot

# ~ print(num_nodes)

# Initialize lists to store the values
initial_node_sizes_values = []
final_node_sizes_values = []

# Iterate over each row in the DataFrame
for index, row in df1.iterrows():
    print(row)
    print(row['initial_node_sizes'])
    # Convert the string representation of the list to an actual list for both columns
    initial_node_sizes_list = ast.literal_eval(row['initial_node_sizes'])
    final_node_sizes_list = ast.literal_eval(row['final_node_sizes'])
    
    # Append the lists to the respective lists
    initial_node_sizes_values.append(initial_node_sizes_list)
    final_node_sizes_values.append(final_node_sizes_list)
num_nodes=len(initial_node_sizes_values)
print(num_nodes)

# Plot bars
# ~ print("Initial Node Sizes:")
df = None
value1 = []
value2 = []
categories = []
algs = []
for a, limit in enumerate(zip(initial_node_sizes_values, final_node_sizes_values)):
    line_initial = limit[0]
    line_final = limit[1]
    #value1 = []
    #value2 = []
    for value_initial, value_final in zip(line_initial, line_final):
        value1.append(value_initial/1000000)
        value2.append((value_initial - value_final)/1000000)
        categories = ['HDD-1', 'HDD-2', 'HDD-3', 'HDD-4', 'HDD-5', 'HDD-6', 'HDD-7', 'HDD-8', 'HDD-9', 'HDD-10']
        algs.append(a)

df = pd.DataFrame({'Category': categories*2, 'Value1': value1, 'Value2': value2, 'Algorithm': algs})

df_1 = df.loc[df['Algorithm'] == 0].reset_index()
df_2 = df.loc[df['Algorithm'] == 1].reset_index()

df = df_1.merge(df_2, left_on='Category', right_on='Category', suffixes=['_0', '_1'])

# Change font of plot to Times
plt.rcParams.update({
    # ~ "text.usetex": True,
    # ~ "font.family": 'Times New Roman',
    # ~ "font.family": 'times',
    "xtick.color": 'grey',
    "ytick.color": 'grey'
})

# Initialize the matplotlib figure
algos = [0, 1]

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
    plt.savefig('plot/' + mode + '/storage_distribution_'  + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')
    
else:
    # ~ plt.figure(figsize=(8, 4))
    for a in algos:
        # ~ fig, ax = plt.subplots()
        plt.figure(figsize=(8, 4))
        # Plot the first set of bars
        sns.barplot(
            x='Category',
            y=f'Value1_{a}',
            data=df,
            # ~ ax=ax,
            color='#1a80bb',
            edgecolor='black',
            linewidth=1.5,
            label='Storage space'
        )
        ## label = 'Value 1'

        # Plot the second set of bars on top of the first set
        sns.barplot(
            x='Category',
            y=f'Value2_{a}',
            data=df,
            # ~ ax=ax,
            color='#ea801c',
            # ~ bottom=value1[10*a: 10*a + 10],
            bottom=0,
            edgecolor='black',
            linewidth=1.5,
            label='Used storage'
        )

        plt.ylabel('Size (TB)')
        plt.xlabel(str(df1['algorithm'][a]))
        plt.legend()
        plt.savefig('plot/' + mode + '/storage_distribution_'  + str(number_input_data) + '_' + str(data_size) + 'MB_' + str(df1['algorithm'][a]) + '.pdf')
