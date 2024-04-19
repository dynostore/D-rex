import numpy as np
import os
import re

DIR_DATA = "../data/"

class RealRecords(object):
    
    def __init__(self, dir_data=DIR_DATA):
        self.dir_data = dir_data
        self.files = self.get_files_in_directory(self.dir_data)
        self.sizes = []
        self.data_dict = {}
        for i,f in enumerate(self.files):
            size = int(re.sub("[^0-9]", "", f))
            self.sizes.append(size)
            self.data_dict[size] = self.load_data(os.path.join(self.dir_data + f))
        
        #self.data = [self.load_data(os.path.join(self.dir_data + f))  for f in self.files]
        #self.data_dict = dict(zip(self.sizes, self.data))

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

