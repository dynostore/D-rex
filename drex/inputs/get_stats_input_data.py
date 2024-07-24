import pandas as pd
import sys

def main(file_path):
    # Read the data into a DataFrame
    df = pd.read_csv(file_path)

    # Calculate the sum of the 'size' column for each Access Type
    total_size_read = df[df['Access Type'] == 1]['size'].sum()
    total_size_write = df[df['Access Type'] == 2]['size'].sum()

    print(f"The sum of the values in the 'size' column for Access Type 1 (read) is: {total_size_read}")
    print(f"The sum of the values in the 'size' column for Access Type 2 (write) is: {total_size_write}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 get_stats_input_data.py <file_path>")
    else:
        file_path = sys.argv[1]
        main(file_path)
