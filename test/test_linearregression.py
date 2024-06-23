from drex.utils.prediction import Predictor
from drex.utils.load_data import RealRecords
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

n = 10
k = 3
file_size = 1000

pred = Predictor()
data = pred.real_records.data


data_to_plot = list()

for s in pred.real_records.sizes:
    Y = pred.real_records.data[pred.real_records.data['size']
                                       == s]['avg_time']
    X = pred.real_records.data[pred.real_records.data['size'] == s][[
                'n', 'k']] 
    size_data = list()
    time_data = list()
    labels = list()
    for x in X.index:
        if X['n'][x] - 2 == X['k'][x]:
            size_data.append(X['n'][x] * int(s) / X['k'][x])
            time_data.append(Y[x])
            #str = f"{X['n'][x]}"
            str = f"{int(X['n'][x])},{int(X['k'][x])}"
            labels.append(str)
    #print(X_str)
    plt.figure(figsize=(10, 6))  # width: 10 inches, height: 6 inches

    plt.scatter(time_data, size_data, color = "blue")
    
    for i in range(len(time_data)):
        plt.annotate(labels[i], (time_data[i], size_data[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)

    
    # Add title and labels
    plt.title('Sample Scatter Plot')
    plt.xlabel('Avg. time (ms)')
    plt.ylabel('Storage overhead (MB)')
    plt.xticks(rotation=45)

    plt.savefig(f"scatter_{s}MBv2.png")
    plt.clf()

#for d in data.index:
    #print(d)
    #print(data["size"][d])
    #data_to_plot.append([data["size"][d], f"{data['n'][d]}-{data['k'][d]}", data["avg_time"][d]])
    
#print(data_to_plot)

# To manage the real time obtained in experiments
#real_records = RealRecords(dir_data="data/")

#frames = []
#sizes = []
#for s in real_records.sizes:
#    data_from_csv = pd.read_csv('data/' + str(s) + 'MB.csv', sep='\t')
#    frames.append(data_from_csv)
#    sizes.extend([s]*len(data_from_csv))
#data = pd.concat(frames)
#data.insert(0, 'size', sizes)

#X = data[['size', 'n', 'k']]
#Y = data['avg_time']

#Xs_test = []
#eal_points = []
#for i in range(3, n):
#    Xs_test.append([file_size, i, 2])
    
#real_points = data[(data["k"] == 2) & (data["size"] == file_size)]

#Xs_test = np.array(Xs_test)
#X_test = np.array([file_size, n, k]).reshape(1, -1)


#pred = Predictor()
#for i in range(3, n):
#    bandwiths = [10] * i
#    print(i,2,pred.predict(file_size, i, 2, bandwiths))

# Create an instance of the LinearRegression class
#reg = LinearRegression()
#reg = Ridge(alpha=0.8)
# Fit the model to the data
#reg.fit(X.values, Y.values)
 
# Print the coefficients of the model
#print(reg.coef_)

#Y_pred = reg.predict(Xs_test)

#print(Y_pred)
#print(Xs_test[:,1])
#print(Y_pred)
#print(len(Xs_test), len(Y_pred))

# plt.scatter(real_points["n"], real_points["avg_time"], color = "blue")
# plt.scatter(Xs_test[:,1], Y_pred, color = "green")
# plt.show()
# Formatting the data into a single dataframe
#sizes = [np.array([s]*len(real_records.data_dict[s])) for s in real_records.sizes]
#for i,s in enumerate(real_records.sizes):
    #np.c_[ real_records.data_dict[s], sizes[i] ]  
    #real_records.data_dict[s]["size"] = sizes[i]
#data = np.hstack([real_records.data_dict[s] for s in real_records.sizes])


# Split the data into independent variables (X) and the dependent variable (Y)



# # Read nearest size
# vals_abs = np.argsort([abs(x-file_size) for x in real_records.sizes])
# nearest_size = real_records.sizes[vals_abs[0]]
# print("Near size:", )

# #Get only the data for the nearest size
# data_for_regression = real_records.data_dict[nearest_size]

# #Filter to get only k equals to 10
# data_for_regression = data_for_regression[(data_for_regression["k"] == k)]

# # Create and train the model
# model = LinearRegression()
# model.fit(data_for_regression["n"].reshape(-1,1), data_for_regression["avg_time"].reshape(-1,1))

# # Predict their corresponding y values
# y_future = model.predict(np.array([[n]]))


# # Plot the original data
# plt.scatter(data_for_regression["n"], data_for_regression["avg_time"], color = "blue")

# # Plot the extrapolated points
# plt.scatter(np.array([[n]]), y_future, color = "green")

# # Show the plot
# plt.show()