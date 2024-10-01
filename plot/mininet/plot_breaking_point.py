import pandas as pd
import matplotlib.pyplot as plt
import glob
import sys
import csv
import shutil
import os

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

# Create a plot figure
plt.figure(figsize=(10, 6))

# Downsampling factor (you can adjust this to control how many points are plotted)
downsample_factor = 1000

# Read all the files matching output_*alg_name*_times.csv
files = glob.glob(f"{folder_path}/*_times.csv")
seconds_in_a_day = 86400  # 60 * 60 * 24
# Loop over each file and plot the data
for file in files:
    # Extract the algorithm name from the file name
    alg_name = file.split('/')[-1].replace('_times.csv', '')
    # Read the data
    df = pd.read_csv(file)

    # Downsample by taking every nth row
    df_downsampled = df.iloc[::downsample_factor, :]
    df_downsampled['Time_in_days'] = df_downsampled['Time'] / seconds_in_a_day
    # Plot the downsampled data (convert Size_stored to MB)
    plt.plot(df_downsampled['Time_in_days'], df_downsampled[' Size_stored'], label=f'{alg_name}')

# Plot the node failure times as vertical lines
for _, row in failures_df.iterrows():
    failed_time_in_days = row['failed_time'] / seconds_in_a_day
    plt.axvline(x=failed_time_in_days, color='r', linestyle='--', label=f'Node {int(row["failed_time"])} failure' if _ == 0 else "")

# Add labels and title
plt.xlabel('Time (days)')
plt.ylabel('Size Stored (MB)')
plt.title('Size Stored Over Time with Node Failures (Downsampled)')
plt.legend(loc='best')

# Show grid
plt.grid(True)

# Display the plot
plt.tight_layout()
plt.savefig(folder_path + '/breaking_point_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + ".pdf")
