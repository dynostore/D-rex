from sklearn.linear_model import LinearRegression
import numpy as np

from drex.utils.load_data import RealRecords
from drex.utils.tool_functions import calculate_transfer_time


class Predictor():

    def __init__(self) -> None:
        self.real_records = RealRecords(dir_data="data/")

        X = self.real_records.data[['size', 'n', 'k']]
        Y = self.real_records.data['avg_time']

        # Create an instance of the LinearRegression class
        self.reg = LinearRegression()

        # Fit the model to the data
        self.reg.fit(X.values, Y.values)

    def predict(self, file_size, n, k, bandwiths):
        Xs_test = np.array([file_size, n, k]).reshape(1, -1)
        Y_pred = self.reg.predict(Xs_test)
        transfer_time = calculate_transfer_time(file_size, max(bandwiths))
        return Y_pred + transfer_time

    def get_model(self):
        return self.reg

    def get_data(self):
        return self.real_records["data"]

    def get_real_records(self):
        return self.real_records
