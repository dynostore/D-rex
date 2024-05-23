# python3 plot/plot.py number_input_data data_size
# python3 plot/plot.py 10 1

import pandas as pd
import matplotlib.pyplot as plt
import sys
import shutil
import os

number_input_data = int(sys.argv[1])
data_size = int(sys.argv[2])

# Move csv
# ~ shutil.move("../D-Rex-Simulation-experiments/src/outputtimes.csv", "plot/data/outputtimes_" + str(number_input_data) + "_" + str(number_input_data) + "MB.csv")

# Load the data from the CSV file
file_path = "plot/data/outputtimes_" + str(number_input_data) + "_" + str(number_input_data) + "MB.csv"
df = pd.read_csv(file_path)

# Rename algorithms with "_reduced_complexity" to "_rc"
df['algorithm'] = df['algorithm'].str.replace('_reduced_complexity', '_rc')

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
plt.bar(df['algorithm'], df['total_storage_used'], color=get_colors(df['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Storage Used')
plt.title('Total Storage Used (MB)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('plot/total_storage_used.pdf')

# Plotting total_simulation_time
plt.figure(figsize=(10, 6))
plt.bar(df['algorithm'], df['total_simulation_time'], color=get_colors(df['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Simulation Time')
plt.title('Total Simulation Time (ms)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('plot/total_simulation_time.pdf')

# Plotting total_chunking_time
plt.figure(figsize=(10, 6))
plt.bar(df['algorithm'], df['total_chunking_time'], color=get_colors(df['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Chunk Time')
plt.title('Total Chunk Time (ms)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('plot/total_chunk_time.pdf')

# Plotting total_upload_time
plt.figure(figsize=(10, 6))
plt.bar(df['algorithm'], df['total_upload_time'], color=get_colors(df['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Upload Time')
plt.title('Total Upload Time (ms)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('plot/total_upload_time.pdf')

# Plotting total_scheduling_time
plt.figure(figsize=(10, 6))
plt.bar(df['algorithm'], df['total_scheduling_time'], color=get_colors(df['algorithm']))
plt.xlabel('Algorithm')
plt.ylabel('Total Scheduling Time')
plt.title('Total Scheduling Time (ms)')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('plot/total_scheduling_time.pdf')
