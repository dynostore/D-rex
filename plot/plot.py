# python3 plot/plot.py number_input_data data_size
#   
# python3 plot/plot.py 10 1
# python3 plot/plot.py 1 10
# python3 plot/plot.py 1 100

import pandas as pd
import matplotlib.pyplot as plt
import sys
import shutil
import os

number_input_data = int(sys.argv[1])
data_size = int(sys.argv[2])

# Copy csv files
shutil.copy("../D-Rex-Simulation-experiments/src/outputtimes.csv", "plot/data/outputtimes_" + str(number_input_data) + "_" + str(data_size) + "MB.csv")
shutil.copy("../D-Rex-Simulation-experiments/src/outputfiles.csv", "plot/data/outputfiles_" + str(number_input_data) + "_" + str(data_size) + "MB.csv")

# Load the data from the CSV files
file_path1 = "plot/data/outputtimes_" + str(number_input_data) + "_" + str(data_size) + "MB.csv"
file_path2 = "plot/data/outputfiles_" + str(number_input_data) + "_" + str(data_size) + "MB.csv"
df1 = pd.read_csv(file_path1)
df2 = pd.read_csv(file_path2)

# Rename algorithms with "_reduced_complexity" to "_rc"
df1['algorithm'] = df1['algorithm'].str.replace('_reduced_complexity', '_rc')
df2['algorithm'] = df2['algorithm'].str.replace('_reduced_complexity', '_rc')

# Define colors
colors = {
    'alg1': 'blue',
    'alg2': 'blue',
    'alg3': 'blue',
    'alg4': 'blue',
    'random': 'green',
    'hdfs': 'green',
    'alg2_rc': 'blue',
    'alg3_rc': 'blue',
    'alg4_rc': 'blue',
    'hdfsrs_3_2': 'green',
    'hdfsrs_6_3': 'green',
    'hdfsrs_10_4': 'green',
    'vandermonders_3_2': 'green',
    'vandermonders_6_3': 'green',
    'vandermonders_10_4': 'green'
}

# Function to get colors based on algorithm names
def get_colors(algorithms):
    return [colors.get(alg, 'gray') for alg in algorithms]

# Plotting total_storage_used
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['total_storage_used'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Storage Used')
plt.title('Total Storage Used (MB)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('plot/total_storage_used_' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')

# Plotting total_simulation_time
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['total_simulation_time'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Simulation Time')
plt.title('Total Simulation Time (ms)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('plot/total_simulation_time_' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')

# Plotting total_chunking_time
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['total_chunking_time'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Chunk Time')
plt.title('Total Chunk Time (ms)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('plot/total_chunk_time_' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')

# Plotting total_upload_time
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['total_upload_time'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Upload Time')
plt.title('Total Upload Time (ms)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('plot/total_upload_time_' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')

# Plotting total_scheduling_time
plt.figure(figsize=(10, 6))
plt.bar(df1['algorithm'], df1['total_scheduling_time'], color=get_colors(df1['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Scheduling Time')
plt.title('Total Scheduling Time (ms)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('plot/total_scheduling_time_' + str(number_input_data) + '_' + str(data_size) + 'MB.pdf')
