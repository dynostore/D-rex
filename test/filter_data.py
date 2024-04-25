import pandas as pd

# Load data from a CSV file
df = pd.read_csv('data/10MB.csv', sep="\t")  # Replace 'your_file.csv' with the actual file path

# Remove rows where k = 1
filtered_df = df[df['k'] != 1]

# Save the filtered DataFrame to a new CSV file
filtered_df.to_csv('data/10MB.csv', index=False, sep="\t")  # Replace 'filtered_data.csv' with the desired file name

print("Filtered data saved successfully.")
