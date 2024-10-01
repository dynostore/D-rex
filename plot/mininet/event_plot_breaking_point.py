import pandas as pd
import matplotlib.pyplot as plt
import glob
import sys
import csv
import shutil
import os
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


def is_int(value):
    try:
        int(value)
        return True
    except ValueError:
        return False
        
data_duration_on_system = int(sys.argv[1])
reliability_threshold = float(sys.argv[2])
mode = sys.argv[3]
plot_type = sys.argv[4]
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
    number_input_data = 0
    with open(input_data, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
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

files_to_move = [
    ("output_alg1_c_times.csv", folder_path + "/alg1_times.csv"),
    ("output_alg4_1_times.csv", folder_path + "/drex_times.csv"),
    ("output_alg_bogdan_times.csv", folder_path + "/algbogdan_times.csv"),
    ("output_daos_1_0_c_times.csv", folder_path + "/daos10_times.csv"),
    ("output_daos_2_0_c_times.csv", folder_path + "/daos20_times.csv"),
    ("output_glusterfs_0_0_c_times.csv", folder_path + "/glusterfs00_times.csv"),
    ("output_glusterfs_6_4_c_times.csv", folder_path + "/gluster64c_times.csv"),
    ("output_hdfs_3_replication_c_times.csv", folder_path + "/hdfs3replication_times.csv"),
    ("output_hdfs_rs_0_0_c_times.csv", folder_path + "/hdfsrs00_times.csv"),
    ("output_hdfs_rs_3_2_c_times.csv", folder_path + "/hdfsrs32_times.csv"),
    ("output_hdfs_rs_4_2_c_times.csv", folder_path + "/hdfsrs42_times.csv"),
    ("output_hdfs_rs_6_3_c_times.csv", folder_path + "/hdfsrs63_times.csv"),
]

for src, dest in files_to_move:
    try:
        move_file_if_exists(src, dest)
    except FileNotFoundError as e:
        print(e)  # Continue to the next file

# Folder path where the files are stored

# Read the node failures file
folder_path_failures = 'drex/inputs/nodes/' + input_nodes_to_print + '_failure_' + input_data_to_print + '_' + str(number_of_loops) + '.csv'
print("folder_path_failures:", folder_path_failures)
failures_df = pd.read_csv(folder_path_failures)


downsample_factor=1



# Create a plot figure
plt.figure(figsize=(10, 4))  # Reduced height for compactness

# Read all the files matching output_*alg_name*_times.csv
files = glob.glob(f"{folder_path}/*_times.csv")
seconds_in_a_day = 86400  # 60 * 60 * 24

# Create a dictionary to map each algorithm to a y-axis position
alg_positions = {file.split('/')[-1].replace('_times.csv', ''): i for i, file in enumerate(files)}
num_algorithms = len(alg_positions)

# Create y-ticks and spread algorithms between 0 and 1 on y-axis
yticks = np.arange(num_algorithms)
yticklabels = list(alg_positions.keys())

# Initialize an empty list to store all data sizes across all schedulers
all_data_sizes = []

# First, gather all data sizes across all schedulers to compute global_max
for file in files:
    df = pd.read_csv(file)
    all_data_sizes.append(df[['Time', ' Size_stored']])

# Combine all data sizes into a single DataFrame
combined_df = pd.concat(all_data_sizes)
combined_df = combined_df.groupby('Time').max().reset_index()

# Compute global_max but ensure that values cannot decrease over time
global_max = combined_df.set_index('Time')[' Size_stored'].reindex(combined_df['Time']).fillna(0)

# Initialize the running maximum
current_max = global_max.iloc[0]

# Ensure global_max is non-decreasing by using a running maximum
for i in range(1, len(global_max)):
    current_max = max(current_max, global_max.iloc[i])  # Update the running maximum
    global_max.iloc[i] = current_max  # Assign the running maximum to the current value

# Plot each algorithm's data
for file in files:
    # Extract the algorithm name from the file name
    alg_name = file.split('/')[-1].replace('_times.csv', '')
    y_position = alg_positions[alg_name]  # Use integer positions to ensure proper alignment
    
    # Read the data
    df = pd.read_csv(file)
    
    # Downsample by taking every nth row
    df_downsampled = df.iloc[::downsample_factor, :]
    
    # Merge the downsampled data with the global maximum to calculate the percentage
    df_downsampled = df_downsampled.merge(global_max, on='Time', suffixes=('', '_global'))
    df_downsampled['Percentage_stored'] = (df_downsampled[' Size_stored'] / df_downsampled[' Size_stored_global']) * 100

    # Variables to track failure progression for this algorithm
    failure_times = []
    percentage_values = []
    
    # Plot line segments for each node failure based on the percentage of data stored
    node_failures = 0  # Reset node failures for each algorithm
    for _, failure in failures_df.iterrows():
        failed_time = failure['failed_time']
        
        # Get the data for this timestamp
        failure_row = df_downsampled[df_downsampled['Time'] <= failed_time].iloc[-1]
        percentage = failure_row['Percentage_stored']
        
        # Append the failure time and percentage to the list
        failure_times.append(node_failures)
        percentage_values.append(percentage)
        
        # Increment the failure counter
        node_failures += 1

    # Plot the failure progression for this algorithm
    for i in range(1, len(failure_times)):
        if percentage_values[i] == 0:
            color = 'gray'  # Use gray for 0%
        else:
            color = 'green' if percentage_values[i] == 100 else 'orange'
        linestyle = 'solid' if percentage_values[i] == 100 else 'dotted'
        
        plt.plot([failure_times[i-1], failure_times[i]], [y_position, y_position], 
                 color=color, linestyle=linestyle, lw=2)

# Add labels and title
plt.xlabel('Number of Node Failures')
plt.yticks(yticks, yticklabels)  # Align the y-ticks with algorithms
plt.title('Event Plot of Node Failures and Data Retention')

# Show grid
plt.grid(True)

# Display the plot
plt.tight_layout()
plt.savefig(folder_path + '/event_plot_with_global_max_array_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")
