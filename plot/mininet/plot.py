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

# Function to calculate slowdowns for a given scheduler
def calculate_slowdown(scheduler_df, optimal_df):
    scheduler_df['slowdown_transfer'] = (scheduler_df['Transfer_Time_Parralelized'] + scheduler_df['Chunking_Time'])
    scheduler_df['slowdown_read'] = (scheduler_df['Read_Time_Parralelized'] + scheduler_df['Reconstruct_Time'])
    
    return scheduler_df

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
    max_N = int(sys.argv[8])
    node_removal = int(sys.argv[9])
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

if node_removal != 0:
    folder_path = "plot/" + mode + "/" + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + "_" + str(number_of_loops) + "_max" + str(max_N) + "_node_removal"
else:
    folder_path = "plot/" + mode + "/" + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + "_" + str(reliability_threshold) + "_" + str(number_of_loops) + "_max" + str(max_N)
create_folder(folder_path)

if mode != "mininet" and mode != "drex_only":
    print("mode must be drex_only or mininet")

files_to_move = [
    ("output_alg1_c_stats.csv", folder_path + "/alg1_c.csv"),
    ("output_alg4_1_stats.csv", folder_path + "/alg4_1.csv"),
    ("output_alg_bogdan_stats.csv", folder_path + "/alg_bogdan.csv"),
    ("output_daos_1_0_c_stats.csv", folder_path + "/daos_1_0_c.csv"),
    ("output_daos_2_0_c_stats.csv", folder_path + "/daos_2_0_c.csv"),
    ("output_glusterfs_0_0_c_stats.csv", folder_path + "/glusterfs_0_0_c.csv"),
    ("output_glusterfs_6_4_c_stats.csv", folder_path + "/gluster_fs_6_4_c.csv"),
    ("output_hdfs_3_replication_c_stats.csv", folder_path + "/hdfs_3_replication_c.csv"),
    ("output_hdfs_rs_0_0_c_stats.csv", folder_path + "/hdfs_rs_0_0_c.csv"),
    ("output_hdfs_rs_3_2_c_stats.csv", folder_path + "/hdfs_rs_3_2_c.csv"),
    ("output_hdfs_rs_4_2_c_stats.csv", folder_path + "/hdfs_rs_4_2_c.csv"),
    ("output_hdfs_rs_6_3_c_stats.csv", folder_path + "/hdfs_rs_6_3_c.csv"),
    ("output_optimal_schedule.csv", folder_path + "/output_optimal_schedule.csv"),
    ("output_optimal_schedule_stats.csv", folder_path + "/optimal_schedule.csv"),
    ("output_random_c_stats.csv", folder_path + "/random_c.csv")
]

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
    
    for src, dest in files_to_move:
        try:
            move_file_if_exists(src, dest)
        except FileNotFoundError as e:
            print(e)  # Continue to the next file
        
    # Load the data from the CSV file
    file_path1 = folder_path + "/output_drex_only_" + input_nodes_to_print + "_" + input_data_to_print + "_" + str(number_of_loops) + ".csv"
