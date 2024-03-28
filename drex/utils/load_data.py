import numpy as np
import os
import re

DIR_DATA = "../data/"

class RealRecords(object):
    
    def __init__(self, dir_data=DIR_DATA):
        self.dir_data = dir_data
        self.files = self.get_files_in_directory(self.dir_data)
        self.sizes = [int(re.sub("[^0-9]", "", f)) for f in self.files]
        self.data = [self.load_data(os.path.join(self.dir_data + f))  for f in self.files]

    # Get files in directory
    def get_files_in_directory(self, directory):
        files = []
        for file in os.listdir(directory):
            if file.endswith(".csv"):
                files.append(file)
        return files

    # Load data into a numpy array
    def load_data(self, file):
        data = np.genfromtxt(file, delimiter="\t", names=True)
        return data

