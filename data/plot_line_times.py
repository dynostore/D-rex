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

# ~ # Nice figs
plt.style.use("/home/gonthier/Chicago/paper.mplstyle")
pt = 1./72.27
jour_sizes = {"PRD": {"onecol": 246.*pt, "twocol": 510.*pt},
              "CQG": {"onecol": 374.*pt},}
my_width = jour_sizes["PRD"]["twocol"]
golden = (1 + 5 ** 0.5) / 2

# Load the data from both files (assuming space-separated values; adjust delimiter if needed)
df1 = pd.read_csv(input_file1)  # assuming default delimiter
df2 = pd.read_csv(input_file2, delimiter='\t')  # tab-separated

# Convert avg_time from milliseconds to seconds for both datasets
df1['avg_time_s'] = df1['avg_time'] / 1000.0
df2['avg_time_s'] = df2['avg_time'] / 1000.0

# Filter the data where K = N - 2 for both datasets
filtered_df1 = df1[df1['k'] == df1['n'] - 2]
filtered_df2 = df2[df2['k'] == df2['n'] - 2]

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

# Create the figure
plt.figure(figsize=(my_width, my_width/golden))

# First file: Decoding overhead
plt.plot(filtered_df1['n'], filtered_df1['avg_time_s'], marker='o', linestyle='-', color='b', label='Decoding overhead')

# Second file: Encoding overhead
plt.plot(filtered_df2['n'], filtered_df2['avg_time_s'], marker='s', linestyle='--', color='r', label='Encoding overhead')

# Set Y-axis limit to start from 0
plt.ylim(0,)

# Add labels and title
plt.xlabel('N (Number of Nodes)')
plt.ylabel('CPU Time (seconds)')

# Show legend and save the figure as PDF
plt.legend(loc='best')
plt.tight_layout()

# Save the plot as PDF
plt.savefig("EC_times.pdf")
