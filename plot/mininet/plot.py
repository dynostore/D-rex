# python3 plot/plot.py number_input_data data_size
#   
# python3 plot/mininet/plot.py 10 1 mininet
# python3 plot/mininet/plot.py 1 10 mininet
# python3 plot/mininet/plot.py 1 100 mininet
# python3 plot/mininet/plot.py 10 200 mininet
# python3 plot/mininet/plot.py 10 100 mininet

import pandas as pd
import matplotlib.pyplot as plt
import sys
import shutil
import os

number_input_data = int(sys.argv[1])
data_size = int(sys.argv[2])
mode = sys.argv[3] # mininet or drex_only

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
    # Copy csv file
    shutil.copy("output_drex_only.csv", "plot/drex_only/data/output_drex_only_" + str(number_input_data) + "_" + str(data_size) + "MB.csv")
    
    # Load the data from the CSV file
    file_path1 = "plot/drex_only/data/output_drex_only_" + str(number_input_data) + "_" + str(data_size) + "MB.csv"

df1 = pd.read_csv(file_path1)

# Rename algorithms
df1['algorithm'] = df1['algorithm'].str.replace('_reduced_complexity', '_rc')
df1['algorithm'] = df1['algorithm'].str.replace('alg1', 'Min Storage')
df1['algorithm'] = df1['algorithm'].str.replace('alg4', 'D-rex')
df1['algorithm'] = df1['algorithm'].str.replace('hdfs_three_replications', '3 replications')
df1['algorithm'] = df1['algorithm'].str.replace('hdfsrs_3_2', 'HDFS RS(3,2)')
df1['algorithm'] = df1['algorithm'].str.replace('hdfsrs_6_3', 'HDFS RS(6,3)')
df1['algorithm'] = df1['algorithm'].str.replace('glusterfs_6_4', 'GlusterFS')

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


# Plot for both minient and drex_only
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


# ~ ++ plot for perfect bw transfer taking max for each data and then sum for all data
