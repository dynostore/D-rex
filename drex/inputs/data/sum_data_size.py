import pandas as pd
import sys

# Load the CSV file
df = pd.read_csv(sys.argv[1])

# Filter the DataFrame where 'Access Type' is 2
filtered_df = df[df['Access Type'] == 2]

# Sum the values in the second column (index 1) for the filtered DataFrame
total_sum = filtered_df.iloc[:, 1].sum()
num_rows = filtered_df.shape[0]
print("Total sum of values in the second column where Access Type is 2:", total_sum)
print("Number of rows with Access Type 2:", num_rows)
