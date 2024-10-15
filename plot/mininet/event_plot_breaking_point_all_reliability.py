import pandas as pd
import matplotlib.pyplot as plt
import glob
import csv
import sys
import os
import numpy as np

def create_folder(folder_path):
    try:
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

downsample_factor = 1

data_duration_on_system = int(sys.argv[1])
mode = sys.argv[2]
plot_type = sys.argv[3]
input_nodes = sys.argv[4]
if is_int(sys.argv[5]):
    number_input_data = int(sys.argv[5])
    data_size = int(sys.argv[6])
    input_data_to_print = str(number_input_data) + "_" + str(data_size)
else:
    input_data = sys.argv[5]
    number_of_loops = int(sys.argv[6])
    max_N = int(sys.argv[7])
    node_removal = int(sys.argv[8])
    input_data_to_print = input_data.split('/')[-1]
    input_data_to_print = input_data_to_print.rsplit('.', 1)[0]
    number_input_data = 0
    with open(input_data, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Access Type'] == '2':
                number_input_data += 1
    number_input_data *= number_of_loops
print(number_input_data, "input data")

input_nodes_to_print = input_nodes.split('/')[-1]
input_nodes_to_print = input_nodes_to_print.rsplit('.', 1)[0]

reliability_thresholds = [0.9, 0.99, 0.999, 0.9999, 0.99999]
# ~ reliability_thresholds = [0.9]

# Create a plot figure
plt.figure(figsize=(10, 6))

# Initialize a dictionary to hold y-ticks positions for each algorithm
alg_y_positions = {}
alg_colors = {}

# Iterate over each reliability threshold
for reliability_threshold in reliability_thresholds:
    folder_path_failures = f'drex/inputs/nodes/{input_nodes_to_print}_failure_{input_data_to_print}_{number_of_loops}.csv'
    failures_df = pd.read_csv(folder_path_failures)

    # Determine the folder path for this reliability threshold
    if node_removal != 0:
        folder_path = f"plot/{mode}/{input_nodes_to_print}_{input_data_to_print}_{data_duration_on_system}_{reliability_threshold}_{number_of_loops}_max{max_N}_node_removal"
    else:
        folder_path = f"plot/{mode}/{input_nodes_to_print}_{input_data_to_print}_{data_duration_on_system}_{reliability_threshold}_{number_of_loops}_max{max_N}"

    # Read all the files matching output_*alg_name*_times.csv for this reliability threshold
    files = glob.glob(f"{folder_path}/*_times.csv")
    
    # Create a dictionary to map each algorithm to a y-axis position
    for file in files:
        alg_name = file.split('/')[-1].replace('_times.csv', '')
        
        # Initialize or update y-positions for this algorithm
        if alg_name not in alg_y_positions:
            alg_y_positions[alg_name] = len(alg_y_positions) * (len(reliability_thresholds) + 1)
            alg_colors[alg_name] = plt.cm.tab10(len(alg_y_positions))  # Assign a distinct color

# Plot each algorithm's data for each reliability threshold
for idx, reliability_threshold in enumerate(reliability_thresholds):
    
    # Determine the folder path for this reliability threshold
    if node_removal != 0:
        folder_path = f"plot/{mode}/{input_nodes_to_print}_{input_data_to_print}_{data_duration_on_system}_{reliability_threshold}_{number_of_loops}_max{max_N}_node_removal"
    else:
        folder_path = f"plot/{mode}/{input_nodes_to_print}_{input_data_to_print}_{data_duration_on_system}_{reliability_threshold}_{number_of_loops}_max{max_N}"

    files = glob.glob(f"{folder_path}/*_times.csv")
    
    # Gather all data sizes across all schedulers to compute global_max
    all_data_sizes = []
    
    for file in files:
        df = pd.read_csv(file)
        all_data_sizes.append(df[['Time', ' Size_stored']])

    combined_df = pd.concat(all_data_sizes)
    combined_df = combined_df.groupby('Time').max().reset_index()

    global_max = combined_df.set_index('Time')[' Size_stored'].reindex(combined_df['Time']).fillna(0)

    current_max = global_max.iloc[0]

    for i in range(1, len(global_max)):
        current_max = max(current_max, global_max.iloc[i])
        global_max.iloc[i] = current_max

    for file in files:
        alg_name = file.split('/')[-1].replace('_times.csv', '')
        
        df = pd.read_csv(file)

        df_downsampled = df.iloc[::downsample_factor, :]

        df_downsampled = df_downsampled.merge(global_max, on='Time', suffixes=('', '_global'))
        df_downsampled['Percentage_stored'] = (df_downsampled[' Size_stored'] / df_downsampled[' Size_stored_global']) * 100

        failure_times = []
        percentage_values = []

        node_failures = 0
        for _, failure in failures_df.iterrows():
            failed_time = failure['failed_time']
            failure_row = df_downsampled[df_downsampled['Time'] <= failed_time].iloc[-1]
            percentage = failure_row['Percentage_stored']
            
            failure_times.append(node_failures)
            percentage_values.append(percentage)
            # ~ if (reliability_threshold == 0.999):
            print(node_failures, "reliability", reliability_threshold, alg_name, "%", percentage)
            
            node_failures += 1

        y_position_base_index=alg_y_positions[alg_name] + idx
        
        for i in range(1, len(failure_times)):
            # Set color to white if percentage is 0, otherwise use algorithm's color
            if percentage_values[i] == 0:
                linestyle_line='dotted'
                color_line = 'white' 
            else:
                color_line = alg_colors[alg_name]
                linestyle_line='solid'
            
            # Calculate line width proportional to the percentage of data stored
            # Assuming a base width of 1 and a maximum width of 4
            base_width = 1
            max_width = 8
            line_width = base_width + (max_width - base_width) * (percentage_values[i] / 100)
            
            plt.plot(
                [failure_times[i-1], failure_times[i]], 
                [y_position_base_index, y_position_base_index], 
                color=color_line, 
                linestyle=linestyle_line,  # Use solid lines for all
                lw=line_width  # Set line width based on percentage
            )
    
        # ~ for i in range(1, len(failure_times)):
            # ~ if percentage_values[i] == 0:
                # ~ color_line = 'white'
            # ~ else:
                # ~ color_line=alg_colors[alg_name]
            # ~ linestyle_line='solid' if percentage_values[i] == 100 else 'dotted'
            
            # ~ plt.plot([failure_times[i-1], failure_times[i]], [y_position_base_index, y_position_base_index], 
                     # ~ color=color_line, linestyle=linestyle_line, lw=4)  # Increased line width
        
        # ~ for i in range(1, len(failure_times)):
            # ~ if percentage_values[i] == 0:
                # ~ color_line = 'gray'
            # ~ else:
                # ~ color_line = colors[idx] if percentage_values[i] == 100 else 'orange'
            # ~ linestyle_line = 'solid' if percentage_values[i] == 100 else 'dotted'
            
            # ~ plt.plot([failure_times[i-1], failure_times[i]], [y_position_base_index, y_position_base_index], 
                     # ~ color=color_line, linestyle=linestyle_line, lw=4)

# Add labels and title
plt.xlabel('Number of Node Failures')
plt.yticks(
   [pos + idx for pos in alg_y_positions.values() for idx in range(len(reliability_thresholds))],
   [f"{alg} ({reliability})" for alg in alg_y_positions.keys() for reliability in reliability_thresholds]
)
plt.title('Event Plot of Node Failures and Data Retention Across Reliability Thresholds')

# Show grid and legend
plt.grid(True)

# Display the plot
plt.tight_layout()
output_folder_path="plot/combined"
create_folder(output_folder_path)
plt.savefig(output_folder_path + '/event_plot_with_global_max_array_' + input_nodes_to_print + "_" + input_data_to_print + "_" + str(data_duration_on_system) + ".pdf")
