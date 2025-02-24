
import os
import pandas as pd
import matplotlib.pyplot as plt
import csv
import re
import sys
import numpy as np
from matplotlib.ticker import LogLocator
from functools import partial
import matplotlib.patches as mpatches
from matplotlib.container import BarContainer  # Import BarContainer

def create_folder(folder_path):
    try:
        os.makedirs(folder_path, exist_ok=True)
    except Exception as e:
        print(f"An error occurred: {e}")

# Prompt the user for the folder suffix
folder_suffix = sys.argv[1]  # This will be the part of the folder name after the set of nodes

if folder_suffix == "_MEVA_merged_365_-1.0_25_max0":
    total_possible_size_to_store = 487000*25
elif folder_suffix == "_MEVA_merged_365_-1.0_250_max0":
    total_possible_size_to_store = 487000*250
elif folder_suffix == "_FB_merged_365_-1.0_1_max0":
    total_possible_size_to_store = 928000000*1
else:
    print("Error suffix", folder_suffix, "not known")
    exit(1)

# Nice figs
plt.style.use("/home/gonthier/Chicago/paper.mplstyle")
pt = 1./72.27
jour_sizes = {"PRD": {"onecol": 246.*pt, "twocol": 510.*pt},
              "CQG": {"onecol": 374.*pt},}
my_width = jour_sizes["PRD"]["twocol"]
golden = (1 + 5 ** 0.5) / 2
# ~ golden = (1 + 5 ** 0.5) / 1.5 # Smaller height
golden = (1 + 5 ** 0.5) / 2.4 # Higher height
plt.rcParams.update({
    'axes.labelsize': 14,       # Axis label font size
    'legend.fontsize': 14,      # Legend font size
    'xtick.labelsize': 14,      # X-axis tick label font size
})

base_dir = 'plot/drex_only'
set_of_node_regex = re.compile(r'^(.+)' + re.escape(folder_suffix) + r'$')

# Combined plot for 'size_stored' as bars and 'throughput' (renamed from efficiency) as hashed bars
metric_to_plot_bars = 'size_stored'
metric_to_plot_efficiency = 'efficiency'

colors = ['#1f77b4', '#17becf','#ffbf00', '#7f7f7f', '#800000', '#d62728', '#ff7f0e', '#2ca02c']
order = [0, 2, 1, 3, 4, 6, 7]  # The new order for labels (C first, A second, B third)

data = []
throughput_optimal_all = []
improvements_alg4 = {}       # For alg4_1.csv vs others
improvements_alg_bogdan = {} # For alg_bogdan.csv vs others

data = []
df_data = []
df = []
throughput_optimal_all = []
# Traverse through each folder
for folder in os.listdir(base_dir):
    folder_path = os.path.join(base_dir, folder)
    if os.path.isdir(folder_path):
        match = set_of_node_regex.search(folder)
        if match:
            print(folder_path)
            set_of_nodes = match.group(1)
            print(f"Set of nodes: {set_of_nodes}")
            
            # ~ # Get optimal data
            # ~ with open(folder_path + "/output_optimal_schedule.csv", mode='r') as file:
                # ~ csv_reader = csv.reader(file)
                # ~ next(csv_reader)
                # ~ throughput_optimal = 0
                # ~ for row in csv_reader:
                    # ~ number_of_data_stored_optimal = int(row[0])
                    # ~ total_storage_used_optimal = float(row[1])
                    # ~ best_upload_time_optimal = float(row[2])
                    # ~ best_read_time_optimal = float(row[3])
                    # ~ size_stored_optimal = float(row[4])
                    
                    # ~ throughput_optimal += size_stored_optimal / (best_upload_time_optimal + best_read_time_optimal)
                # ~ print("throughput_optimal:", throughput_optimal)
                # ~ throughput_optimal_all.append(throughput_optimal)
                
            # --- New Code Block: Compare throughput of all CSV files against alg4_1.csv ---
            csv_files = {}
            for file in os.listdir(folder_path):
                if file.endswith('.csv') and not file.startswith('output_drex_only_') and not file.startswith('output_optimal_schedule') and not file.startswith('optimal_schedule'):
                    file_path = os.path.join(folder_path, file)
                    print("Open", file_path)
                    df_temp = pd.read_csv(file_path, quotechar='"', doublequote=True, skipinitialspace=True)
                    # Calculate throughput as: Size / (Transfer_Time_Parralelized + Chunking_Time + Read_Time_Parrallelized + Reconstruct_Time)
                    df_temp['throughput'] = df_temp['Size'] / (
                            df_temp['Transfer_Time_Parralelized'] +
                            df_temp['Chunking_Time'] +
                            df_temp['Read_Time_Parralelized'] +
                            df_temp['Reconstruct_Time']
                        )
                    csv_files[file] = df_temp
                
            # ~ differences = {}
            # Check that the reference file exists
            if 'alg4_1.csv' in csv_files:
                reference_df = csv_files['alg4_1.csv']
                diffs_alg4 = {}
                for file_name, df_other in csv_files.items():
                    if file_name != 'alg4_1.csv':
                        # Only compare up to the smallest number of lines between the two files
                        n_lines = min(len(reference_df), len(df_other))
                        # Compute throughput difference line-by-line
                        throughput_ref = reference_df['throughput'].iloc[:n_lines].values
                        throughput_other = df_other['throughput'].iloc[:n_lines].values
                        throughput_diff = throughput_ref - throughput_other
                        avg_diff = throughput_diff.mean()
                        # ~ differences[file_name] = avg_diff
                        diffs_alg4[file_name] = avg_diff
                        # ~ print(f"Comparison between alg4_1.csv and {file_name}: Average throughput difference = {avg_diff:.3f}")
                improvements_alg4[folder] = diffs_alg4
            else:
                print("Reference file alg4_1.csv not found in", folder_path)

            # Compute differences using alg_bogdan.csv as the reference
            if 'alg_bogdan.csv' in csv_files:
                ref_df = csv_files['alg_bogdan.csv']
                diffs_bogdan = {}
                for file_name, df_other in csv_files.items():
                    if file_name != 'alg_bogdan.csv':
                        n_lines = min(len(ref_df), len(df_other))
                        throughput_ref = ref_df['throughput'].iloc[:n_lines].values
                        throughput_other = df_other['throughput'].iloc[:n_lines].values
                        diff = throughput_ref - throughput_other
                        avg_diff = diff.mean()
                        diffs_bogdan[file_name] = avg_diff
                        # ~ print(f"[{folder}] alg_bogdan.csv vs {file_name}: Avg throughput diff = {avg_diff:.3f}")
                improvements_alg_bogdan[folder] = diffs_bogdan
            else:
                print(f"Reference file alg_bogdan.csv not found in {folder_path}")
                
def create_improvement_figure(improvements, ref_label, out_filename):
    # --- Renaming dictionary ---
    rename_dict = {
        'alg1_c': 'GreedyMinStorage', 'alg4_1': 'D-Rex SC',
        'hdfs_3_replication_c': '3 Replication', 'hdfsrs_3_2': 'EC(3,2)',
        'hdfsrs_6_3': 'EC(6,3)', 'glusterfs_6_4': 'EC(4,2)',
        'Min_Storage_c': 'Min_Storage', 'alg_bogdan': 'D-Rex LB',
        'glusterfs_6_4_c': 'EC(4,2)', 'glusterfs_0_0_c': 'EC(4,2)',
        'GlusterFS_c': 'EC(4,2)', 'hdfs_rs_3_2_c': 'EC(3,2)',
        'hdfs_rs_6_3_c': 'EC(6,3)', 'hdfs_rs_4_2_c': 'HDFS(4,2)',
        'hdfs_rs_0_0_c': 'HDFS_RS_ADAPTATIVE', 'random_c': 'Random',
        'daos_1_0_c': 'DAOS', 'daos_2_0_c': 'DAOS_2R', 'least_used_node': 'GreedyLeastUsed'
    }
    # --- Exclude these algorithms (after renaming) ---
    exclude_list = ['HDFS(4,2)', 'GlusterFS_ADAPTATIVE', 'DAOS_2R', 'HDFS_RS_ADAPTATIVE', '3 Replication']
    # --- Desired order from left to right ---
    desired_order = ['D-Rex SC', 'D-Rex LB', 'GreedyMinStorage', 'GreedyLeastUsed', 'EC(3,2)', 'EC(4,2)', 'EC(6,3)', 'DAOS']
    # --- Colors mapping ---
    algorithm_colors = {
        'D-Rex SC': '#1f77b4',
        'D-Rex LB': '#17becf',
        'GreedyMinStorage': '#ffbf00',
        'GreedyLeastUsed': '#7f7f7f',
        'EC(3,2)': '#800000',
        'EC(4,2)': '#d62728',
        'EC(6,3)': '#ff7f0e',
        'DAOS': '#2ca02c'
    }
    
    n_folders = len(improvements)
    if n_folders == 0:
        print(f"No data for {ref_label}. Skipping plot.")
        return
    # Arrange subplots in a grid: using 2 columns for 4 folders (or more generally, ceil(n_folders/2) rows)
    ncols = 2
    nrows = int(np.ceil(n_folders / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 6, nrows * 4))
    if n_folders == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    
    for idx, (ax, (folder, diffs)) in enumerate(zip(axes, improvements.items())):
        # --- Process each diff dictionary for the folder ---
        # Rename file keys (remove .csv and use rename_dict) and exclude unwanted algorithms.
        renamed_diffs = {}
        for file_name, avg_diff in diffs.items():
            base = file_name.replace('.csv', '')
            renamed = rename_dict.get(base, base)
            if renamed in exclude_list:
                continue
            renamed_diffs[renamed] = avg_diff
        
        # Order the algorithms based on our desired order.
        ordered_algs = [alg for alg in desired_order if alg in renamed_diffs]
        avg_diffs = [renamed_diffs[alg] for alg in ordered_algs]
        x_positions = np.arange(len(ordered_algs))
        colors_used = [algorithm_colors[alg] for alg in ordered_algs]
        
        # Plot the bars.
        ax.bar(x_positions, avg_diffs, color=colors_used, alpha=0.7)
        # Draw a horizontal line at 0.
        ax.axhline(0, color='black', linewidth=1)
        # Set the same y-axis limits on all plots.
        ax.set_ylim(-2, 2.5)
        
        # --- Set subplot title based on folder name ---
        if "10_most_used_nodes_" in folder:
            title = "Most Used"
        elif "most_reliable" in folder:
            title = "Most Reliable"
        elif "most_unreliable" in folder:
            title = "Most Unreliable"
        elif "most_used_node_x10_" in folder:
            title = "Homogeneous"
        else:
            title = folder
        ax.set_title(title)
        
        # Show x tick labels (algorithm names) only on the bottom row.
        if idx >= (nrows - 1) * ncols:
            ax.set_xticks(x_positions)
            ax.set_xticklabels(ordered_algs, rotation=45, ha='right')
        else:
            ax.set_xticks(x_positions)
            ax.set_xticklabels([])
        
        # Show the y-axis label only on the left column.
        if idx % ncols == 0:
            ax.set_ylabel('Avg Throughput Difference (MB/s)')
        else:
            ax.set_ylabel('')
            
    # Remove any unused axes.
    for j in range(n_folders, nrows * ncols):
        fig.delaxes(axes[j])
    
    fig.suptitle(f'Improvement of {ref_label} over Other Algorithms', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(out_filename)
    plt.close(fig)

def create_combined_improvement_figure(improvements_sc, improvements_lb, out_filename):
    # Renaming dictionary (for CSV file base names)
    rename_dict = {
        'alg1_c': 'GreedyMinStorage', 'alg4_1': 'D-Rex SC',
        'hdfs_3_replication_c': '3 Replication', 'hdfsrs_3_2': 'EC(3,2)',
        'hdfsrs_6_3': 'EC(6,3)', 'glusterfs_6_4': 'EC(4,2)',
        'Min_Storage_c': 'Min_Storage', 'alg_bogdan': 'D-Rex LB',
        'glusterfs_6_4_c': 'EC(4,2)', 'glusterfs_0_0_c': 'EC(4,2)',
        'GlusterFS_c': 'EC(4,2)', 'hdfs_rs_3_2_c': 'EC(3,2)',
        'hdfs_rs_6_3_c': 'EC(6,3)', 'hdfs_rs_4_2_c': 'HDFS(4,2)',
        'hdfs_rs_0_0_c': 'HDFS_RS_ADAPTATIVE', 'random_c': 'Random',
        'daos_1_0_c': 'DAOS', 'daos_2_0_c': 'DAOS_2R', 'least_used_node': 'GreedyLeastUsed'
    }
    # Exclude these algorithms (after renaming)
    exclude_list = ['D-Rex SC', 'D-Rex LB', 'HDFS(4,2)', 'GlusterFS_ADAPTATIVE', 'DAOS_2R', 'HDFS_RS_ADAPTATIVE', '3 Replication']
    # Desired order (left to right)
    desired_order = ['GreedyMinStorage', 'GreedyLeastUsed', 'EC(3,2)', 'EC(4,2)', 'EC(6,3)', 'DAOS']
    # Color mapping (the two blues for the Drex's, yellow for GreedyMinStorage, gray for GreedyLeastUsed, etc.)
    algorithm_colors = {
        # ~ 'D-Rex SC': '#1f77b4',
        # ~ 'D-Rex LB': '#17becf',
        'GreedyMinStorage': '#ffbf00',
        'GreedyLeastUsed': '#7f7f7f',
        'EC(3,2)': '#800000',
        'EC(4,2)': '#d62728',
        'EC(6,3)': '#ff7f0e',
        'DAOS': '#2ca02c'
    }
    
    # Determine common folders (sets of nodes) for which we have data in both dictionaries.
    common_folders = sorted(set(improvements_sc.keys()).intersection(set(improvements_lb.keys())))
    n_folders = len(common_folders)
    if n_folders == 0:
        print("No common folder data found between the two improvement dictionaries.")
        return
    
    # Arrange subplots: for instance, 2 columns.
    ncols = 2
    nrows = int(np.ceil(n_folders / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 6, nrows * 4))
    if n_folders == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    
    # Loop over each folder.
    for idx, folder in enumerate(common_folders):
        ax = axes[idx]
        # Retrieve the improvement dictionaries for this folder.
        diffs_sc = improvements_sc[folder]
        diffs_lb = improvements_lb[folder]
        
        # Process the keys: remove '.csv' and rename.
        renamed_sc = {}
        for file_name, val in diffs_sc.items():
            base = file_name.replace('.csv', '')
            renamed = rename_dict.get(base, base)
            if renamed in exclude_list:
                continue
            renamed_sc[renamed] = val
        renamed_lb = {}
        for file_name, val in diffs_lb.items():
            base = file_name.replace('.csv', '')
            renamed = rename_dict.get(base, base)
            if renamed in exclude_list:
                continue
            renamed_lb[renamed] = val
        
        # Determine the set of algorithms to plot (order according to desired_order).
        all_algs = set(renamed_sc.keys()).union(set(renamed_lb.keys()))
        ordered_algs = [alg for alg in desired_order if alg in all_algs]
        M = len(ordered_algs)
        if M == 0:
            print(f"No valid algorithms for folder {folder}")
            continue
        
        # X positions: one group per algorithm.
        x = np.arange(M)
        bar_width = 0.35  # width of each bar
        offset = bar_width / 2  # to place two bars side by side
        
        # Get improvement values for each algorithm (or NaN if missing).
        sc_values = [renamed_sc.get(alg, np.nan) for alg in ordered_algs]
        lb_values = [renamed_lb.get(alg, np.nan) for alg in ordered_algs]
        
        # Plot D-Rex SC bars (left side of group).
        bars_sc = ax.bar(x - offset, sc_values, width=bar_width,
                         color=[algorithm_colors[alg] for alg in ordered_algs],
                         edgecolor='black', linewidth=0.5, label='D-Rex SC')
        # Plot D-Rex LB bars (right side of group) with a hatch pattern.
        bars_lb = ax.bar(x + offset, lb_values, width=bar_width,
                         color=[algorithm_colors[alg] for alg in ordered_algs],
                         edgecolor='black', linewidth=0.5, hatch='//', label='D-Rex LB')
        
        # Draw a horizontal line at 0.
        ax.axhline(0, color='black', linewidth=1)
        # Set uniform y-axis limits.
        ax.set_ylim(-2, 2.5)
        # Set x-axis ticks at group centers.
        ax.set_xticks(x)
        # Only show x-axis tick labels on bottom row.
        if idx < (nrows - 1) * ncols:
            ax.set_xticklabels([])
        else:
            ax.set_xticklabels(ordered_algs, rotation=45, ha='right')
        # Show y-axis label only on left column subplots.
        if idx % ncols == 0:
            ax.set_ylabel('Avg Throughput Difference (MB/s)')
        else:
            ax.set_ylabel('')
        
        # Set subplot title based on folder name contents.
        folder_lower = folder.lower()
        if "10_most_used_nodes_" in folder:
            title = "Most Used"
        elif "most_reliable" in folder:
            title = "Most Reliable"
        elif "most_unreliable" in folder:
            title = "Most Unreliable"
        elif "most_used_node_x10_" in folder:
            title = "Homogeneous"
        elif "sentinal" in folder_lower:
            title = "Sentinal"
        elif "fb" in folder_lower:
            title = "FB"
        elif "ibm" in folder_lower:
            title = "IBM"
        else:
            title = folder
        ax.set_title(title)
        
        # Optionally, add a legend on the first subplot.
        if idx == 0:
            ax.legend()
    
    # Remove any unused axes.
    for j in range(n_folders, nrows * ncols):
        fig.delaxes(axes[j])
    
    fig.suptitle('Combined Improvement of D-Rex SC and LB over Other Algorithms', fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(out_filename)
    plt.close(fig)
    
# Create figure for improvements using alg4_1.csv as reference
create_improvement_figure(improvements_alg4, "alg4_1.csv", os.path.join("plot", "combined", f"alg4_improvement_all{folder_suffix}.pdf"))

# Create figure for improvements using alg_bogdan.csv as reference
create_improvement_figure(improvements_alg_bogdan, "alg_bogdan.csv", os.path.join("plot", "combined", f"alg_bogdan_improvement_all{folder_suffix}.pdf"))

# Create the combined one
create_combined_improvement_figure(improvements_alg4, improvements_alg_bogdan, "plot/combined/combined_throughput_different_set_of_nodes_improvements_drex.pdf")
