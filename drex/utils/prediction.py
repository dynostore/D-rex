from sklearn.linear_model import LinearRegression, Lasso, Ridge
import numpy as np

from drex.utils.load_data import RealRecords
from drex.utils.tool_functions import calculate_transfer_time


class Predictor():

    def __init__(self) -> None:
        self.real_records = RealRecords(dir_data="data/")
        # self.target_size = target_size
        # vals_abs = np.argsort([abs(x-self.target_size) for x in self.real_records.sizes])
        # self.nearest_sizes = [self.real_records.sizes[i] for i in vals_abs[:1]]
        # self.data_to_use = self.real_records.data[self.real_records.data['size'].isin(self.nearest_sizes)]
        # self.data_to_use.loc[:,("avg_time")] = self.data_to_use.loc[:,("avg_time")].apply(lambda x: x * target_size / self.nearest_sizes[0])
        self.models = {}
        for s in self.real_records.sizes:
            X = self.real_records.data[self.real_records.data['size'] == s][[
                'n', 'k']]
            Y = self.real_records.data[self.real_records.data['size']
                                       == s]['avg_time']
            self.models[s] = LinearRegression(fit_intercept=True)
            self.models[s].fit(X.values, Y.values)
        # Create an instance of the LinearRegression class
        # self.reg = LinearRegression(fit_intercept=True)
        # self.reg = Ridge(alpha=0.8, solver='auto')

        # Fit the model to the data
        # self.reg.fit(X.values, Y.values)

    def predict(self, file_size, n, k, bandwiths):
        nearest_size = min(self.real_records.sizes,
                           key=lambda x: abs(x-file_size))
        Xs_test = np.array([n, k]).reshape(1, -1)
        Y_pred = self.models[nearest_size].predict(Xs_test)[0] * file_size / nearest_size
        transfer_time = calculate_transfer_time(file_size, max(bandwiths))
        return Y_pred + transfer_time

    def get_model(self):
        return self.reg

    def get_data(self):
        return self.real_records["data"]

    def get_real_records(self):
        return self.real_records
