import pandas as pd
import sys

def main(file_paths, output_path):
    # Read the data from all files into DataFrames
    dataframes = [pd.read_csv(file_path) for file_path in file_paths]

    # Concatenate all DataFrames
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Sort the DataFrame by 'Relative Time'
    combined_df.sort_values(by='Relative Time (s)', inplace=True)

    # Save the result to a new CSV file
    combined_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python merge_and_sort.py <file1_path> <file2_path> ... <output_path>")
    else:
        *file_paths, output_path = sys.argv[1:]
        main(file_paths, output_path)

# ~ import pandas as pd
# ~ import sys
# ~ import os

# ~ def sort_and_save_chunks(file_path, chunk_size=100000):
    # ~ chunk_list = []
    # ~ for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        # ~ chunk_list.append(chunk.sort_values(by='Relative Time (s)'))
    # ~ sorted_file_path = f"{file_path}_sorted"
    # ~ pd.concat(chunk_list).to_csv(sorted_file_path, index=False)
    # ~ return sorted_file_path

# ~ def merge_sorted_files(file_paths, output_file, chunk_size=100000):
    # ~ temp_files = [sort_and_save_chunks(file) for file in file_paths]
    # ~ merged_df = pd.concat((pd.read_csv(file) for file in temp_files))
    # ~ merged_df = merged_df.sort_values(by='Relative Time (s)')
    # ~ merged_df.to_csv(output_file, index=False)
    # ~ for temp_file in temp_files:
        # ~ os.remove(temp_file)

# ~ if __name__ == "__main__":
    # ~ if len(sys.argv) < 3:
        # ~ print("Usage: python3 merge_files.py <output_file> <file1> <file2> ... <fileN>")
    # ~ else:
        # ~ output_file = sys.argv[1]
        # ~ input_files = sys.argv[2:]
        # ~ merge_sorted_files(input_files, output_file)
