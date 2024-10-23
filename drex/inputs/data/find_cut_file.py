import pandas as pd
import sys

def find_cut_line(csv_file, target_value):
    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Filter DataFrame where 'Access Type' is 2
    # ~ filtered_df = df[df['Access Type'] == 2]

    # Initialize a cumulative sum
    cumulative_sum = 0

    # Iterate through the rows of the filtered DataFrame
    for index, row in df.iterrows():
        if row[4] == 2:
            cumulative_sum += row[1]  # Add the value from the second column

            # Check if the cumulative sum matches the target value
            if cumulative_sum >= target_value:
                # Output the index after which to cut (1-based line number)
                print(f"Cut after line {index + 1}")
                return
    
    # If the cumulative sum does not reach the target value
    print("The target value cannot be reached with the sum of column 2 for Access Type 2.")

# Example usage
if __name__ == "__main__":
    # Pass the CSV file and the target value as arguments
    csv_file = sys.argv[1]  # Replace with your actual CSV file path
    target_value = int(sys.argv[2])      # Replace with the desired target sum

    find_cut_line(csv_file, target_value)
