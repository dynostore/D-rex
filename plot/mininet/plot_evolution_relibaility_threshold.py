# python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_used_nodes_MEVA_merged_365_ _20
# python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_unreliable_nodes_MEVA_merged_365_ _250

import os
import pandas as pd
import matplotlib.pyplot as plt
import re
import sys
import numpy as np
from matplotlib.ticker import LogLocator
from functools import partial

def create_folder(folder_path):
    try:
        # Create the folder if it does not exist
        os.makedirs(folder_path, exist_ok=True)
        print(f"Folder '{folder_path}' is ready.")
    except Exception as e:
        print(f"An error occurred: {e}")

def count_decimal_places(value):
    # Convert the value to a string and split by the decimal point
    value_str = str(value)
    if '.' in value_str:
        # Get the part after the decimal point and count its length
        return len(value_str.split('.')[1])
    else:
        # If there's no decimal point, return 0
        return 0
# Prompt the user for folder name parts before and after the reliability threshold
folder_prefix = sys.argv[1]
folder_suffix = sys.argv[2]

# Base directory where your folders are located
# ~ base_dir = 'plot/drex_only'
base_dir = 'plot/drex_only/with_old_strat_26_08'
# Regular expression to extract reliability threshold from folder name
threshold_regex = re.compile(re.escape(folder_prefix) + r'(\d+\.\d+)' + re.escape(folder_suffix))
# List of metrics to plot
metrics_to_plot = ['total_chunking_time', 'total_storage_used', 'total_parralelized_upload_time', 'mean_storage_used', 'total_upload_time', 'number_of_data_stored', 'combined_mean_upload_chunk', 'combined_total_upload_chunk']
markers = ['o', 's', 'D', '^', 'v', '>', '<', 'p', 'h', '*']

for metric in metrics_to_plot:
    plt.figure(figsize=(10, 6))
    index = 0
    data = []
    df_data = []
    df = []
    # Traverse through each folder
    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if os.path.isdir(folder_path):
            # Extract reliability threshold from the folder name
            match = threshold_regex.search(folder)
            if match:
                reliability_threshold = float(match.group(1))
                index = count_decimal_places(reliability_threshold)

                # Read all CSV files in the folder
                for file in os.listdir(folder_path):
                    if file.endswith('.csv'):
                        file_path = os.path.join(folder_path, file)
                        df = pd.read_csv(file_path, quotechar='"', doublequote=True, skipinitialspace=True)
                        
                        # If plotting the combined metric
                        if metric == 'combined_mean_upload_chunk':
                            df['combined_mean_upload_chunk'] = df['mean_parralelized_upload_time'] + df['mean_chunking_time']
                        if metric == 'combined_total_upload_chunk':
                            df['combined_total_upload_chunk'] = df['total_parralelized_upload_time'] + df['total_chunking_time']
                        
                        # Fetch the algorithm names and corresponding mean_chunking_time
                        for i, algorithm in enumerate(df['algorithm']):
                            value = df[metric].iloc[i]
                            # ~ data.append((reliability_threshold, algorithm, mean_chunking_time))
                            data.append((index, algorithm, value))

    # Convert the data into a DataFrame
    df_data = pd.DataFrame(data, columns=['Reliability Threshold', 'Algorithm', metric])

    # Rename algorithms
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('_reduced_complexity', '_rc')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('alg1', 'Min_Storage')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('alg4', 'D-rex')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_three_replications', '3_replications')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_3_replication_c', 'hdfs_3_replications')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfsrs_3_2', 'HDFS_RS(3,2)')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfsrs_6_3', 'HDFS_RS(6,3)')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('glusterfs_6_4', 'GlusterFS')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('Min_Storage_c', 'Min_Storage')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('alg_bogdan', 'Greedy_Load_Balancing')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('glusterfs_6_4_c', 'GlusterFS')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('GlusterFS_c', 'GlusterFS')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_3_2_c', 'HDFS_RS(3,2)')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_6_3_c', 'HDFS_RS(6,3)')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('random_c', 'Random')

    # Sort the DataFrame by Reliability Threshold in increasing order
    df_data = df_data.sort_values(by='Reliability Threshold')

    # Filter out rows where the value is 0 in the column you want to plot
    df_data = df_data[df_data[metric] != 0]
    i = 0
    # Iterate over each algorithm and plot its trend
    for algorithm in df_data['Algorithm'].unique():
        subset = df_data[df_data['Algorithm'] == algorithm]
        subset = subset.sort_values(by='Reliability Threshold')
        plt.plot(subset['Reliability Threshold'], subset[metric], marker=markers[i % len(markers)], label=algorithm)
        i += 1


    # Set custom x-tick labels
    # ~ new_labels = ['0.9', '0.99', '0.999', '0.9999', '0.99999', '0.999999', '0.9999999', '0.99999999']
    new_labels = ['0.9', '0.99', '0.999', '0.9999', '0.99999']

    # Apply the new labels to the x-ticks
    # ~ x_values = [1, 2, 3, 4, 5, 6, 7, 8]
    x_values = [1, 2, 3, 4, 5]
    plt.xticks(ticks=x_values, labels=new_labels)

    plt.title('Evolution of ' + metric + ' Depending on Reliability Threshold')
    plt.xlabel('Reliability Threshold')
    plt.ylabel(metric)
    plt.legend()
    plt.grid(True)
    folder_path = "plot/drex_only/" + folder_prefix + "evolution" + folder_suffix
    create_folder(folder_path)

    plt.savefig(folder_path + '/' + metric + '.pdf')


