import matplotlib.pyplot as plt
import numpy as np

# Nice figs
plt.style.use("/home/gonthier/Chicago/paper.mplstyle")
pt = 1./72.27
jour_sizes = {"PRD": {"onecol": 246.*pt, "twocol": 510.*pt},
              "CQG": {"onecol": 374.*pt},}
my_width = jour_sizes["PRD"]["twocol"]
golden = (1 + 5 ** 0.5) / 2
golden = (1 + 5 ** 0.5) / 1.5 # Smaller height
golden = (1 + 5 ** 0.5) / 1.2 # Smaller height
# ~ golden = (1 + 5 ** 0.5) / 2.4 # Higher height
plt.rcParams.update({
    'axes.labelsize': 16,       # Axis label font size
    'legend.fontsize': 16,      # Legend font size
    'xtick.labelsize': 18,      # X-axis tick label font size
})

# Data
methods = ['DS + D-Rex SC', 'DS + D-Rex LB', 'HDFS EC(3,2)', 'HDFS EC(6,3)']
throughput = [30.1, 25.1, 28.3, 25.1]  # Example values, adjust these to match your data

# Bar properties
# ~ colors = ['#1f77b4', '#ffbf00', '#17becf', '#800000', '#d62728', '#ff7f0e', '#7f7f7f']
colors = ['#1f77b4', '#17becf', '#d62728', '#ff7f0e']
bar_width = 0.8

# Create bar chart
fig, ax = plt.subplots(figsize=(my_width, my_width/(golden)))
bars = plt.bar(methods, throughput, color=colors, width=bar_width, edgecolor='black')

# Formatting
plt.ylabel('Writing + Encoding\nThroughput (MB/s)', fontsize=14)
plt.ylim(0, 35)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
# ~ plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)
# ~ ax_bottom.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)

# Show plot
plt.tight_layout()
plt.savefig("plot/combined/real_experiment.pdf")
