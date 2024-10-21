# python3 plot_scatter_times.py input_file

import matplotlib.pyplot as plt
import pandas as pd
import sys
from mpl_toolkits.mplot3d import Axes3D

# Check if the input file was passed as an argument
if len(sys.argv) < 2:
    print("Usage: python script_name.py input_file.csv")
    sys.exit(1)

# Read the input file from the command line argument
input_file = sys.argv[1]

# Load the data from the CSV file into a DataFrame
df = pd.read_csv(input_file)

# Convert avg_time from milliseconds to seconds
df['avg_time_s'] = df['avg_time'] / 1000.0

# Plot the scatter plot with N on the x-axis, K on the y-axis, and avg_time as size
plt.figure(figsize=(10, 7))
plt.scatter(df['n'], df['k'], s=df['avg_time_s'] * 10, c=df['avg_time_s'], cmap='viridis', alpha=0.6, edgecolor='w', linewidth=0.5)

# Add labels and title
plt.xlabel('N (Number of Nodes)')
plt.ylabel('K (Number of Data chunks)')
plt.colorbar(label='Avg Time (seconds)')

# Show plot
plt.tight_layout()
plt.show()
