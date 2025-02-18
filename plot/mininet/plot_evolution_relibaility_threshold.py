# python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_used_nodes_MEVA_merged_365_ _20
# python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_unreliable_nodes_MEVA_merged_365_ _250
# python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_used_nodes_MEVA_merged_365_ _250
# python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_used_nodes_MEVA_merged_365_ _2_max0
# python3 plot/mininet/plot_evolution_relibaility_threshold.py 10_most_used_nodes_MEVA_merged_365_ _25_max6

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import csv
import re
import sys
import numpy as np
from matplotlib.ticker import LogLocator
from functools import partial

def create_folder(folder_path):
    try:
        # Create the folder if it does not exist
        os.makedirs(folder_path, exist_ok=True)
        # ~ print(f"Folder '{folder_path}' is ready.")
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

# Nice figs
plt.style.use("/home/gonthier/Chicago/paper.mplstyle")
pt = 1./72.27
jour_sizes = {"PRD": {"onecol": 246.*pt, "twocol": 510.*pt},
              "CQG": {"onecol": 374.*pt},}
my_width = jour_sizes["PRD"]["twocol"]
golden = (1 + 5 ** 0.5) / 2
# ~ golden = (1 + 5 ** 0.5) / 1.5 # Smaller height
plt.rcParams.update({
    'axes.labelsize': 14,       # Axis label font size
    'legend.fontsize': 14,      # Legend font size
})

print(folder_prefix)
print(folder_suffix)
# Base directory where your folders are located
base_dir = 'plot/drex_only'
# Regular expression to extract reliability threshold from folder name
# ~ threshold_regex = re.compile(re.escape(folder_prefix) + r'(\d+\.\d+)' + re.escape(folder_suffix))
threshold_regex = re.compile(re.escape(folder_prefix) + r'(\d+\.\d+)' + re.escape(folder_suffix) + r'$')
# List of metrics to plot
metrics_to_plot = ['total_chunking_time', 'total_storage_used', 'total_parralelized_upload_time', 'mean_storage_used', 'total_upload_time', 'number_of_data_stored', 'combined_mean_upload_chunk', 'combined_total_upload_chunk',  'combined_total_read_reconstruct', 'combined_mean_reconstruct_read', 'best_fit', 'efficiency', 'size_stored', 'combined_times']
# ~ metrics_to_plot = ['efficiency']

markers = ['o', '^', 's', 'D', '+', 'v', 'h', 'x', '*', 'x', '+', '|', '_', '.', ',', '1', '2', '3', '4']
colors = ['#1f77b4', '#ffbf00', '#17becf', '#2ca02c', '#7f7f7f', '#800000', '#d62728', '#ff7f0e']
order = [0, 2, 1, 3, 5, 6, 4, 7]  # The new order for labels (C first, A second, B third)

for metric in metrics_to_plot:
    plt.figure(figsize=(my_width, my_width/golden))
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
                # ~ print(folder_path)
                reliability_threshold = float(match.group(1))
                index = count_decimal_places(reliability_threshold)
                
                
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
                        print("Read", file);
                        file_path = os.path.join(folder_path, file)
                        df = pd.read_csv(file_path, quotechar='"', doublequote=True, skipinitialspace=True)
                        
                        # If plotting the combined metric
                        if metric == 'combined_mean_upload_chunk':
                            df['combined_mean_upload_chunk'] = df['mean_parralelized_upload_time'] + df['mean_chunking_time']
                        if metric == 'combined_total_upload_chunk':
                            df['combined_total_upload_chunk'] = df['total_parralelized_upload_time'] + df['total_chunking_time']
                        if metric == 'combined_total_read_reconstruct':
                            df['combined_total_read_reconstruct'] = df['total_read_time_parrallelized'] + df['total_reconstruct_time']
                        if metric == 'combined_times':
                            df['combined_times'] = (df['total_read_time_parrallelized'] + df['total_reconstruct_time'] + df['total_parralelized_upload_time'] + df['total_chunking_time'])/3600
                        if metric == 'combined_mean_reconstruct_read':
                            df['combined_mean_reconstruct_read'] = df['mean_read_time_parrallelized'] + df['mean_reconstruct_time']
                        if metric == 'best_fit': # Goal is to get closer to 1
                            df['best_fit'] = best_upload_time_optimal/(df['total_parralelized_upload_time'] + df['total_chunking_time']) + best_read_time_optimal/(df['total_read_time_parrallelized'] + df['total_reconstruct_time']) + df['size_stored']/size_stored_optimal
                        if metric == 'efficiency': # Goal is to maximize
                            df['efficiency'] = df['size_stored']/(df['total_parralelized_upload_time'] + df['total_chunking_time'] + df['total_read_time_parrallelized'] + df['total_reconstruct_time'])
                        
                        # Fetch the algorithm names and corresponding mean_chunking_time
                        for i, algorithm in enumerate(df['algorithm']):
                            # ~ print(i, algorithm)
                            value = df[metric].iloc[i]
                            data.append((index, algorithm, value))

    # Convert the data into a DataFrame
    df_data = pd.DataFrame(data, columns=['Reliability Threshold', 'Algorithm', metric])
        
    # Rename algorithms
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('alg1_c', 'GreedyMinStorage')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('alg4_1', 'D-Rex SC')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_3_replication_c', 'HDFS 3 Rep')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfsrs_3_2', 'EC(3,2)')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfsrs_6_3', 'EC(6,3)')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('glusterfs_6_4', 'GlusterFS')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('Min_Storage_c', 'Min_Storage')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('alg_bogdan', 'D-Rex LB')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('glusterfs_6_4_c', 'EC(4,2)')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('glusterfs_0_0_c', 'GlusterFS_ADAPTATIVE')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('GlusterFS_c', 'EC(4,2)')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_3_2_c', 'EC(3,2)')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_6_3_c', 'EC(6,3)')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_4_2_c', 'HDFS(4,2)')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('hdfs_rs_0_0_c', 'HDFS_RS_ADAPTATIVE')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('random_c', 'Random')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('daos_1_0_c', 'DAOS')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('daos_2_0_c', 'DAOS_2R')
    df_data['Algorithm'] = df_data['Algorithm'].str.replace('least_used_node', 'GreedyLeastUsed')

    # Filter out rows where the value is 0 in the column you want to plot
    df_data = df_data[df_data[metric] != 0]
    i = 0
        
    # Filter out some algorithm
    if metric == 'combined_times':
        algorithms_to_exclude = ['HDFS(4,2)', 'GlusterFS_ADAPTATIVE', 'DAOS_2R', 'HDFS_RS_ADAPTATIVE']
        filtered_df = df_data[~df_data['Algorithm'].isin(algorithms_to_exclude)]
    else:
        filtered_df = df_data

    # Iterate over each algorithm and plot its trend
    i = 0
    for algorithm in filtered_df['Algorithm'].unique():
        subset = filtered_df[filtered_df['Algorithm'] == algorithm]
        subset = subset.sort_values(by='Reliability Threshold')

        # If metric is 'combined_times', only plot the first 7 points
        if metric == 'combined_times':
            subset = subset.head(7)
        if algorithm == 'D-Rex SC' or algorithm == 'D-Rex LB':
            zorder=3
        else:
            zorder=2
        plt.plot(subset['Reliability Threshold'], subset[metric], marker=markers[i], label=algorithm, color=colors[i % len(colors)], zorder=zorder)
        
        i += 1

    # Set custom x-tick labels
    if metric == 'combined_times':
        new_labels = ['0.9', '0.99', '0.999', '0.9999', '0.99999', '0.999999', '0.9999999']
    else:
        new_labels = ['0.9', '0.99', '0.999', '0.9999', '0.99999', '0.999999', '0.9999999', '0.99999999', '0.999999999']

    # Apply the new labels to the x-ticks
    if metric == 'combined_times':
        x_values = [1, 2, 3, 4, 5, 6, 7]
    else:
        x_values = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    plt.xticks(ticks=x_values, labels=new_labels)

    plt.xlabel('Minimum Reliability Requirement')
    if metric == 'combined_times':
        plt.ylabel('Duration of Data Operations (h)')
        # ~ plt.ylim(0,)
        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend([handles[idx] for idx in order], [labels[idx] for idx in order], loc='upper center', bbox_to_anchor=(0.5, -0.11), fancybox=False, ncol=3)
    else:
        plt.title('Evolution of ' + metric + ' Depending on Reliability Threshold')
        plt.ylabel(metric)
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.11), fancybox=False, ncol=4)
    plt.grid(True)
    folder_path = "plot/drex_only/" + folder_prefix + "evolution" + folder_suffix
    create_folder(folder_path)
    print(folder_path, metric)
    plt.savefig(folder_path + '/' + metric + '.pdf')
