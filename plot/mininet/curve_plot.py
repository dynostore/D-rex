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

if mode != "mininet" and mode != "drex_only":
    print("mode must be drex_only or mininet")

folder_path = "plot/drex_only/data/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print
create_folder(folder_path)

if mode == "mininet":
    print("Mode mininet pas encore implémenté dans curve_plot.py")
else:
    # Copy csv file for data
    create_folder(folder_path)
    shutil.copy("output_alg1_stats.csv", "plot/drex_only/data/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "/alg1.csv")
    shutil.copy("output_alg4_stats.csv", "plot/drex_only/data/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "/drex.csv")
    shutil.copy("output_glusterfs_6_4_stats.csv", "plot/drex_only/data/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "/glusterfs_6_4.csv")
    shutil.copy("output_hdfsrs_3_2_stats.csv", "plot/drex_only/data/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "/hdfsrs_3_2.csv")
    shutil.copy("output_hdfsrs_6_3_stats.csv", "plot/drex_only/data/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "/hdfsrs_6_3.csv")
    shutil.copy("output_hdfs_three_replications_stats.csv", "plot/drex_only/data/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "/hdfs_three_replications.csv")
    shutil.copy("output_random_stats.csv", "plot/drex_only/data/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "/random.csv")
    
# Running through all detailed stats file, getting data that have been scheduled by all and plot curves
# Get list of all files in the directory
directory = folder_path
files = [f for f in os.listdir(directory) if f.endswith('.csv')]

# Dictionary to store data frames for each algorithm
data_frames = {}

# Iterate through each file in the directory
for filename in os.listdir(directory):
    if filename.endswith('.csv'):
        algorithm_name = filename[:-4]  # Remove the last 4 characters from the filename
        file_path = os.path.join(directory, filename)
        
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        
        # Store the DataFrame in the dictionary
        data_frames[algorithm_name] = df
        
        print("Read", algorithm_name)

# Find the common IDs across all data frames
common_ids = set.intersection(*[set(df['ID']) for df in data_frames.values()])

# Filter data frames to only include rows with common IDs
# Prepare a dictionary to store the summed chunking times for each algorithm
chunking_times = {algo: {} for algo in data_frames.keys()}

# Sum the chunking times for common IDs
for algo, df in data_frames.items():
    # Filter rows that have IDs in common_ids
    filtered_df = df[df['ID'].isin(common_ids)]
    
    chunking_times[algo] = filtered_df.iloc[:, 4].values

# Plotting
plt.figure(figsize=(12, 8))

# Plot the chunking times for each algorithm
for algo, times in chunking_times.items():
    sorted_indices = sorted(range(len(times)), key=lambda i: list(common_ids)[i])
    sorted_times = [times[i] for i in sorted_indices]
    sorted_ids = sorted(common_ids)
    
    # Calculate cumulative sum of chunking times
    cumulative_times = np.cumsum(sorted_times)
    
    # Plot the cumulative chunking times
    plt.plot(sorted_ids, cumulative_times, label=algo)

plt.xlabel('ID')
plt.ylabel('Chunking Time')
plt.title('Chunking Time for Different Algorithms')
plt.legend()
plt.grid(True)
folder_path = "plot/" + mode + "/" + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold)
plt.savefig(folder_path + '/curve' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")
