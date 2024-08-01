# Start an exec for a single algorithm

# Imports
import numpy as np
from drex.utils.load_data import RealRecords
from drex.utils.prediction import Predictor
from drex.utils.tool_functions import *
from drex.schedulers.random import *
from drex.schedulers.algorithm1 import *
from drex.schedulers.algorithm2 import *
from drex.schedulers.algorithm3 import *
from drex.schedulers.algorithm4 import *
from drex.schedulers.glusterfs import *
from drex.schedulers.hdfs import *
from drex.utils.tool_functions import probability_of_failure
import sys
import itertools
import time
import csv

# Parsing args
alg = sys.argv[1]
next_arg = 4
if alg == "hdfsrs" or alg == "vandermonders" or alg == "glusterfs":
    RS1 = int(sys.argv[4])
    RS2 = int(sys.argv[5])
    next_arg = 6
    print("Algo:", alg, RS1, RS2)
else:
    print("Algo:", alg)
input_nodes = sys.argv[next_arg]
# ~ print("Input nodes from file:", input_nodes)

# Initialize lists and constants
node_sizes = []
write_bandwidths = []
read_bandwidths = []
annual_failure_rates = []
data_duration_on_system = int(sys.argv[2]) # In days
reliability_threshold = float(sys.argv[3]) # threshold we want to meet
real_records = RealRecords(dir_data="data/") # To manage the real time obtained in experiments
predictor = Predictor()  # Update for different file sizes

print("data_duration_on_system:", data_duration_on_system, "reliability_threshold:", reliability_threshold)

# Read data from CSV file
with open(input_nodes, 'r') as csvfile:
    csvreader = csv.reader(csvfile)
    next(csvreader) # Skip the header row
    for row in csvreader:
        node_sizes.append(int(row[1]))
        write_bandwidths.append(int(row[2]))
        read_bandwidths.append(int(row[3]))
        annual_failure_rates.append(float(row[4]))
number_of_nodes = len(node_sizes)
set_of_nodes = list(range(0, number_of_nodes))
reliability_nodes = [probability_of_failure(annual_failure_rates[i], data_duration_on_system) for i in range(0, number_of_nodes)]
max_node_size = max(node_sizes)
total_storage_size = sum(node_sizes)
# ~ print("There are", number_of_nodes, "nodes:")
# ~ print("Sizes:", node_sizes)
# ~ print("Write bandwidths:", write_bandwidths)
print("Nodes failure probability:", reliability_nodes)

# Read or create input data
set_of_data = []
if sys.argv[next_arg + 1] == "fixed_data":
    number_of_data = int(sys.argv[next_arg + 2])
    data_size = int(sys.argv[next_arg + 3])
    print("We have", number_of_data, "data of size", data_size)
    set_of_data = [data_size for _ in range(number_of_data)]
else:
    input_data_file = sys.argv[next_arg + 2]
    number_of_repetition = int(sys.argv[next_arg + 3])
    print("Reading input data from file", input_data_file)
    for loop in range(number_of_repetition):
        with open(input_data_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Access Type'] == '2':
                    set_of_data.append(float(row['size']))

# ~ print(set_of_data)
# Start code and fetch results
number_of_data_stored = 0
total_scheduling_time = 0
total_upload_time = 0
total_upload_time = 0
total_parralelized_upload_time = 0
total_N = 0
total_storage_used = 0
differences = []
min_data_size = sys.maxsize
node_sizes_initialy = node_sizes.copy()
counter = 0

for data in set_of_data:
    counter += 1
    if counter % 2500 == 0:
        print(f"Processed {counter} data")

    node_sizes_before = node_sizes.copy()
    
    if data < min_data_size:
        min_data_size = data
    
    if alg == "alg1":
        start = time.time()
        set_of_nodes_chosen, N, K, node_sizes = algorithm1(number_of_nodes, reliability_threshold, reliability_nodes, node_sizes, data)
        end = time.time()
    elif alg == "alg2":
        start = time.time()
        set_of_nodes_chosen, N, K, node_sizes = algorithm2(number_of_nodes, reliability_nodes, write_bandwidths, reliability_threshold, data, real_records, node_sizes, predictor)
        end = time.time()
    elif alg == "alg3":
        start = time.time()
        set_of_nodes_chosen, N, K, node_sizes = algorithm3(number_of_nodes, reliability_nodes, write_bandwidths, reliability_threshold, data, real_records, node_sizes, predictor)
        end = time.time()
    elif alg == "alg4":
        start = time.time()
        set_of_nodes_chosen, N, K, node_sizes = algorithm4(number_of_nodes, reliability_nodes,write_bandwidths, reliability_threshold, data, real_records, node_sizes, max_node_size,min_data_size, system_saturation, total_storage_size, predictor)
        end = time.time()
    elif alg == "alg2_rc":
        start = time.time()
        set_of_nodes_chosen, N, K, node_sizes = algorithm2_work_with_reduced_set_of_nodes(number_of_nodes, reliability_nodes, write_bandwidths, reliability_threshold, data, real_records, node_sizes, predictor)
        end = time.time()
    elif alg == "alg3_rc":
        start = time.time()
        set_of_nodes_chosen, N, K, node_sizes = algorithm3_look_at_reduced_set_of_possibilities(number_of_nodes, reliability_nodes, write_bandwidths, reliability_threshold, data, real_records, node_sizes, predictor)
        end = time.time()
    elif alg == "alg4_rc":
        start = time.time()
        set_of_nodes_chosen, N, K, node_sizes = algorithm4_look_at_reduced_set_of_possibilities(number_of_nodes, reliability_nodes, write_bandwidths, reliability_threshold, data, real_records, node_sizes, max_node_size, min_data_size, system_saturation, total_storage_size, predictor)
        end = time.time()
    elif alg == "random":
        start = time.time()
        set_of_nodes_chosen, N, K, node_sizes = random_schedule(number_of_nodes, reliability_nodes, reliability_threshold, node_sizes, data)
        end = time.time()
    elif alg == "hdfs_three_replications":
        start = time.time()
        set_of_nodes_chosen, N, K, node_sizes = hdfs_three_replications(number_of_nodes, reliability_threshold, reliability_nodes, node_sizes, data, write_bandwidths, "simulation")
        end = time.time()
    elif alg == "hdfsrs":
        start = time.time()
        set_of_nodes_chosen, N, K, node_sizes, size_to_stores = hdfs_reed_solomon(number_of_nodes, reliability_threshold, reliability_nodes, node_sizes, data, write_bandwidths, RS1, RS2)
        end = time.time()
    elif alg == "vandermonders":
        start = time.time()
        set_of_nodes_chosen, N, K, node_sizes, size_to_stores = hdfs_reed_solomon(number_of_nodes, reliability_threshold, reliability_nodes, node_sizes, data, write_bandwidths, RS1, RS2)
        end = time.time()
    elif alg == "glusterfs":
        start = time.time()
        set_of_nodes_chosen, N, K, node_sizes = glusterfs(RS1, RS2, number_of_nodes, reliability_nodes, write_bandwidths, reliability_threshold, data, node_sizes)
        end = time.time()

    total_scheduling_time += end - start
        
    if N != -1: # Else it means that the scheduler could not find a solution that works
        differences = [node_sizes_before[i] - node_sizes[i] for i in range(number_of_nodes)]
        # ~ print("differences:", differences)
        max_upload_time = -1
        for i in range(number_of_nodes):
            # ~ print(differences[i] / write_bandwidths[i])
            upload_time = differences[i] / write_bandwidths[i]
            if (upload_time > max_upload_time):
                max_upload_time = upload_time
            total_upload_time += differences[i] / write_bandwidths[i]
            total_storage_used += differences[i]
        # ~ print("max_upload_time", max_upload_time)
        total_parralelized_upload_time += max_upload_time
        number_of_data_stored += 1
        total_N += N
        
        # ~ print(node_sizes)

# Writing results in a file
# ~ print("total_scheduling_time =", total_scheduling_time, "seconds") 
# ~ print("total_storage_used =", total_storage_used, "MB") 
# ~ print("total_upload_time:", total_upload_time)
# ~ print("total_parralelized_upload_time:", total_parralelized_upload_time)
# ~ print("number_of_data_stored:", number_of_data_stored)

output_filename = 'output_drex_only.csv'
if alg == "hdfsrs" or alg == "vandermonders" or alg == "glusterfs":
    alg_to_print = alg + "_" + str(RS1) + "_" + str(RS2)
else:
    alg_to_print = alg
# Write the values to the output file
print("Writing output in file", output_filename)
with open(output_filename, 'a') as file:
    file.write(f"{alg_to_print}, {total_scheduling_time}, {total_storage_used}, {total_upload_time}, {total_parralelized_upload_time}, {number_of_data_stored}, {total_N}, {total_storage_used/number_of_data_stored}, {total_upload_time/number_of_data_stored}, {total_N/number_of_data_stored}, \"{node_sizes_initialy}\", \"{node_sizes}\"\n")
