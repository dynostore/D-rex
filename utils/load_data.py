import numpy as np
import os
import re

DIR_DATA = "../data/"

# Iterate over files in the directory and load them

# Get files in directory
def get_files_in_directory(directory):
    files = []
    for file in os.listdir(directory):
        if file.endswith(".csv"):
            files.append(file)
    return files

# Load data into a numpy array
def load_data(file):
    print(file)
    data = np.genfromtxt(file, delimiter="\t", names=True)
    return data


files = get_files_in_directory(DIR_DATA)
sizes = [int(re.sub("[^0-9]", "", f)) for f in files]  # Get the size of the file in MB from the filename removing characters
data = [load_data(os.path.join(DIR_DATA + f))  for f in files]

