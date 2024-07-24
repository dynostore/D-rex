import pandas as pd
import sys

def calculate_stats(file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    
    # Convert storage_size from bytes to MB and calculate the sum
    df['storage_size_mb'] = df['storage_size'] / (1024 * 1024)
    total_size_mb = df['storage_size_mb'].sum()
    
    # Calculate the mean of annual_failure_rate
    mean_failure_rate = df['annual_failure_rate'].mean()
    
    # Print the results
    print(f"The sum of the 'storage_size' column in MB is: {total_size_mb:.2f} MB")
    print(f"The mean of the 'annual_failure_rate' column is: {mean_failure_rate:.4f}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 script.py <file_path>")
    else:
        file_path = sys.argv[1]
        calculate_stats(file_path)
