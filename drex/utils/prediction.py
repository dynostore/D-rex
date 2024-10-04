from sklearn.linear_model import LinearRegression, Lasso, Ridge
import numpy as np

from drex.utils.load_data import RealRecords
from drex.utils.tool_functions import calculate_transfer_time


class Predictor():
    """
    Class to predict the time to chunk a file of a given size

    1) Reads times from the real records in the data folder
    2) Fits a linear regression model to the data
    3) Predicts the time to chunk a file of a given size
    4) Returns the prediction
    """

    def __init__(self, dir_data="data/") -> None:
        # Load the real records from data traces
        self.real_records = RealRecords(dir_data=dir_data)
        
        # Object to temporally store the regression models for each file size
        self.models = {}
        
        # Iterate over each file size with real records
        for s in self.real_records.sizes:
            
            # The X values are the the values of n and k
            X = self.real_records.data[self.real_records.data['size'] == s][[
                'n', 'k']]
            
            # The Y value is the average time to chunk the file
            Y = self.real_records.data[self.real_records.data['size']
                                       == s]['avg_time']
            
            # Fit the model and store it in the models dictionary
            self.models[s] = LinearRegression(fit_intercept=True)
            self.models[s].fit(X.values, Y.values)
        

    """
    Receives the file size, n, k and the bandwidths and returns the prediction
    file_size: int - The size of the file to chunk
    n: int - The number of chunks
    k: int - The number of chunks to reconstruct the file
    bandwiths: list - The list of the bandwidths of the nodes
    """
    def predict(self, file_size, n, k, bandwiths):
        # Looks for the model with the nearest size to the file size
        nearest_size = min(self.real_records.sizes,
                           key=lambda x: abs(x-file_size))
        
        # The X values to predict are n and k
        Xs_test = np.array([n, k]).reshape(1, -1)
        
        print(Xs_test)
        
        # Predict the time to chunk the file
        Y_pred = self.models[nearest_size].predict(Xs_test)[0] #* file_size / nearest_size
        transfer_time = calculate_transfer_time(file_size/k, min(bandwiths)) # Min because we take the slowest bandwidth into account. Also I pass the chunk size and not the full data size
        Y_pred = Y_pred/1000 # divided because we want to take seconds just like the transfer_time that is in seconds
        # ~ print(transfer_time, "+", Y_pred)
        return Y_pred #+ transfer_time
        
    def predict_only_chunk_time(self, file_size, n, k):
        nearest_size = min(self.real_records.sizes,
                           key=lambda x: abs(x-file_size))
        Xs_test = np.array([n, k]).reshape(1, -1)
        Y_pred = self.models[nearest_size].predict(Xs_test)[0] * file_size / nearest_size
        Y_pred = Y_pred/1000
        return Y_pred

    def get_model(self):
        return self.reg

    def get_data(self):
        return self.real_records["data"]

    def get_real_records(self):
        return self.real_records
