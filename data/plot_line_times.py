# python3 plot_line_times.py reconstruct/new_c/400MB_with_comma.csv 400MB.csv upload_400MB.csv

import matplotlib.pyplot as plt
import pandas as pd
import sys

# Check if two input files were passed as arguments
if len(sys.argv) < 3:
    print("Usage: python script_name.py input_file1 input_file2")
    sys.exit(1)

# Read the input files from the command line arguments
input_file1 = sys.argv[1]
input_file2 = sys.argv[2]
input_file3 = sys.argv[3]

# Nice figs
plt.style.use("/home/gonthier/Chicago/paper.mplstyle")
pt = 1./72.27
jour_sizes = {"PRD": {"onecol": 246.*pt, "twocol": 510.*pt},
              "CQG": {"onecol": 374.*pt},}
my_width = jour_sizes["PRD"]["twocol"]
golden = (1 + 5 ** 0.5) / 2

# Load the data from both files (assuming space-separated values; adjust delimiter if needed)
df1 = pd.read_csv(input_file1)  # assuming default delimiter
df2 = pd.read_csv(input_file2, delimiter='\t')  # tab-separated
df3 = pd.read_csv(input_file3, delimiter='\t')  # tab-separated

# Convert avg_time from milliseconds to seconds for both datasets
df1['avg_time_s'] = df1['avg_time'] / 1000.0
df2['avg_time_s'] = df2['avg_time'] / 1000.0
df3['avg_time_s'] = df3['avg_time'] / 1000.0

# Filter the data where K = N - 2 for both datasets
filtered_df1 = df1[df1['k'] == df1['n'] - 2]
filtered_df2 = df2[df2['k'] == df2['n'] - 2]
filtered_df3 = df3[df3['k'] == df3['n'] - 2]

# Compute storage overhead for both datasets (assuming k != 0 to avoid division by zero)
filtered_df1['storage_overhead'] = ( 400.0 / filtered_df1['k'] ) * filtered_df1['n']
filtered_df2['storage_overhead'] = ( 400.0 / filtered_df2['k'] ) * filtered_df1['n']
# ~ filtered_df3['storage_overhead'] = ( 400.0 / filtered_df3['k'] ) * filtered_df1['n']

# Set the global font size and line width
plt.rcParams.update({
    'font.size': 14,           # Increase font size for all text elements
    'axes.labelsize': 18,      # Axis labels
    'xtick.labelsize': 16,     # X-axis tick labels
    'ytick.labelsize': 16,     # Y-axis tick labels
    'legend.fontsize': 14,     # Legend text size
    'lines.linewidth': 2.5,    # Line width
    'lines.markersize': 8,     # Marker size
})

# Create the figure and main axis
fig, ax1 = plt.subplots(figsize=(my_width, my_width/golden))

# Plot the time for decoding (first file)
ax1.plot(filtered_df1['n'], filtered_df1['avg_time_s'], marker='o', linestyle='-', color='b', label='Decoding')

# Plot the time for encoding (second file)
ax1.plot(filtered_df2['n'], filtered_df2['avg_time_s'], marker='s', linestyle='--', color='r', label='Encoding')

# Plot upload time
ax1.plot(filtered_df3['n'], filtered_df3['avg_time_s']*filtered_df3['n'], marker='x', linestyle='--', color='orange', label='Uploading')

# Set Y-axis limit to start from 0 for the primary Y-axis
ax1.set_ylim(0,)
ax1.set_xlabel('Total number of chunks')
ax1.set_ylabel('Time (seconds)')
ax1.set_xticks(range(2, 21, 2))
# Create a secondary Y-axis for the storage overhead
ax2 = ax1.twinx()
ax2.bar(filtered_df1['n'], filtered_df1['storage_overhead'], width=0.4, alpha=0.5, color='g', label='Storage overhead')

# Set Y-axis label and limit for the secondary axis
ax2.set_ylabel('Aggregate storage (MB)', color='g')
ax2.set_ylim(0, max(filtered_df1['storage_overhead'].max(), filtered_df2['storage_overhead'].max()) * 1.1)

# Add legends for both axes
ax1.legend(loc='upper left')
ax2.legend(loc='upper center')

# Adjust layout and save the figure
plt.tight_layout()
plt.savefig("EC_times_with_storage_overhead.pdf")
