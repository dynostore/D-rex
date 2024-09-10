# python3 plot_stats_input_nodes.py <input_file>

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import numpy as np

def process_filename(file_path):
    """
    Process the input file path by extracting the filename after the last '/' and removing the last 4 characters.
    
    Args:
    - file_path (str): The input file path as a string.
    
    Returns:
    - str: The modified filename.
    """
    # Find the position of the last '/'
    last_slash_index = file_path.rfind('/')
    
    # Extract the substring after the last '/'
    filename = file_path[last_slash_index + 1:]
    
    # Remove the last 4 characters
    modified_filename = filename[:-4]
    
    return modified_filename

minmax = {}
minmax["min"] = {}
minmax["min"]["storage_size_TB"] = 100000
minmax["min"]["write_bandwidth"] = 100000
minmax["min"]["read_bandwidth"] = 100000
minmax["min"]["annual_failure_rate"] = 100000
minmax["max"] = {}
minmax["max"]["storage_size_TB"] = -1
minmax["max"]["write_bandwidth"] = -1
minmax["max"]["read_bandwidth"] = -1
minmax["max"]["annual_failure_rate"] = -1

def update_minmax(minmax, data, factor):
    minmax["min"][factor] = min(minmax["min"][factor], min(data[factor]))
    minmax["max"][factor] = max(minmax["max"][factor], max(data[factor]))

def read_data(datapath, minmax):
    
    # Load the data into a DataFrame
    data = pd.read_csv(datapath)
    result = process_filename(datapath)

    # Convert storage size to terabytes
    data['storage_size_TB'] = data['storage_size'] / 1_000_000

    update_minmax(minmax, data, "storage_size_TB")
    update_minmax(minmax, data, "write_bandwidth")
    update_minmax(minmax, data, "read_bandwidth")
    update_minmax(minmax, data, "annual_failure_rate")

    # Set the style to 'darkgrid' for a professional look
    # ~ sns.set(palette='gray')
    # Define custom color palette
    color_palette = ['#000000', '#666666', '#999999', '#CCCCCC']

    # 1. Histogram of the distribution of annual failure rate
    plt.figure(figsize=(10, 6))
    # ~ plt.grid(True, which='both', linestyle='--', linewidth=0.5, zorder=1)
    plt.hist(data['annual_failure_rate'], bins=20, edgecolor='black', color='black', alpha=0.7)
    # ~ plt.title('Distribution of Annual Failure Rate')
    plt.xlabel('Annual Failure Rate (%)')
    plt.ylabel('Frequency')
    plt.savefig('drex/inputs/nodes/afr_' + result + '.pdf')

    # 2. Histogram of the distribution of storage sizes
    plt.figure(figsize=(10, 6))
    # ~ plt.grid(True, which='both', linestyle='--', linewidth=0.5, zorder=1)
    plt.hist(data['storage_size_TB'], bins=20, edgecolor='black', color='black', alpha=0.7)
    # ~ plt.title('Distribution of Storage Sizes')
    plt.xlabel('Storage Size (TB)')
    plt.ylabel('Frequency')
    plt.savefig('drex/inputs/nodes/sizes_' + result + '.pdf')

    return data
    
def plot_stats_input_nodes(datapath, data, minmax):

    result = process_filename(datapath)

    # Specify the names for the axes
    x_labels = {
        'storage_size_TB': 'Storage Size (TB)',
        'write_bandwidth': 'Write Bandwidth (MB/s)',
        'read_bandwidth': 'Read Bandwidth (MB/s)',
        'annual_failure_rate': 'Annual Failure Rate (%)'
    }
    y_labels = x_labels
    plt.figure(figsize=(12, 10))
    # Define custom colors
    scatter_color = 'black'
    hist_color = 'black'
    g = sns.pairplot(data[['storage_size_TB', 'write_bandwidth', 'read_bandwidth', 'annual_failure_rate']],
                    plot_kws={'alpha':0.7, 'edgecolor': 'black', 'color': 'black'}, diag_kws={'color': hist_color})  # Use black for histograms)

    # Adjust min max for each axis
    for ax in g.axes.flatten():
        if ax is not None:
            x_label = ax.get_xlabel()
            y_label = ax.get_ylabel()
            print(x_label, y_label)
            if x_label != "":
                ax.set_xlim(minmax['min'][x_label], minmax['max'][x_label])
            if y_label != "":
                ax.set_ylim(minmax['min'][y_label], minmax['max'][y_label])

    # Manually set labels for the top-left subplot
    g.axes[0, 0].set_ylabel('Frequency', fontsize=10)
    # Hide the upper triangle of the plot
    for i in range(len(g.axes)):
        for j in range(len(g.axes)):
            if i < j:
                g.axes[i, j].set_visible(False)
    # Add labels to all subplots
    for ax in g.axes.flatten():
        if ax is not None:
            # Set histogram bars color to black
            for patch in ax.patches:
                patch.set_edgecolor('black')
                patch.set_facecolor(hist_color)
            # Set scatter points color to black
            for line in ax.lines:
                line.set_color(scatter_color)
        
        x_label = ax.get_xlabel()
        y_label = ax.get_ylabel()
        ax.set_xlabel(x_labels.get(x_label, x_label), fontsize=10)
        ax.set_ylabel(y_labels.get(y_label, y_label), fontsize=10)

    # Correct the y-axes for the histogram
    for i in range(len(g.axes)):
        # g.axes[i, i].yaxis.set_label_position("right")
        # g.axes[i, i].yaxis.tick_right()
        g.axes[i, i].set_ylabel("Frequency")
        g.axes[i, i].yaxis.set_tick_params(labelleft=False)

    # Add correlation annotations
    for i, j in zip(*np.tril_indices_from(g.axes, -1)):
        ax = g.axes[i, j]
        if ax is not None:
            x = data.iloc[:, j]
            y = data.iloc[:, i]
    plt.tight_layout()  # Adjust layout to prevent clipping of labels
    plt.savefig('drex/inputs/nodes/correlation_' + result + '.pdf')
    # plt.savefig('drex/inputs/nodes/correlation_' + result + '.png')


data_names = [
    "drex/inputs/nodes/10_most_used_nodes.csv",
    "drex/inputs/nodes/10_most_reliable_nodes.csv",
    "drex/inputs/nodes/10_most_unreliable_nodes.csv",
    "drex/inputs/nodes/all_nodes_backblaze.csv"
]

plot_data = {}

for data_name in data_names:
    plot_data[data_name] = read_data(data_name, minmax)

for data_name in data_names:
    plot_stats_input_nodes(data_name, plot_data[data_name], minmax)

