#~ python3 -m venv venv
#~ . venv/bin/activate
# pip install seaborn

# Truncate current output files and add header
truncate -s 0 output_drex_only.csv
echo "algorithm,total_scheduling_time,total_storage_used,total_upload_time,total_parralelized_upload_time,number_of_data_stored,total_N,mean_storage_used,mean_upload_time,mean_N,initial_node_sizes,final_node_sizes,total_chunking_time,mean_chunking_time,mean_parralelized_upload_time,total_read_time,mean_read_time,total_read_time_parrallelized,mean_read_time_parrallelized,total_reconstruct_time,mean_reconstruct_time,size_stored" > output_drex_only.csv

# Inputs
data_duration_on_system=$1
reliability_threshold=$2
input_nodes=$3

# Number of nodes
number_nodes=$(wc -l < "$input_nodes")
number_nodes=$((number_nodes-1))
echo "$((number_nodes))"

# Input data
if [[ "$4" == *.csv ]]; then
    input_data=$4
    number_of_repetition=$5
    add_data_pattern=$6
    echo "Input nodes: $input_nodes / Input data: $input_data $add_data_pattern"
else
    number_of_data=$4
    data_size=$5
    number_of_repetition=1
    add_data_pattern=$6
    echo "Input nodes: $input_nodes / Input data: $number_of_data data of size $data_size"
fi

remove_node_pattern=$7
fixed_random_seed=$8
max_N=$9
input_nodes_failure_times=${10}
echo ${input_nodes_failure_times}
# Choosing our alg4 version
if [ $number_nodes -ge 1 ]; then
    alg4=alg4_rc
else
    alg4=alg4
fi

make

if [ "$input_nodes" == "drex/inputs/nodes/8_nodes_from_chicago.csv" ]; then
    nodes_to_print=8
elif [ "$input_nodes" == "drex/inputs/nodes/10_nodes_from_chicago.csv" ]; then
    nodes_to_print=10
fi


# Alg 4
./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 4 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} 1
#~ ./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 4 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} 1 > "trace_drex_sc_${reliability_threshold}_${nodes_to_print}.csv"

#~ # Alg LB
./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 5 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times}
#~ ./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 5 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} > "trace_drex_lb_${reliability_threshold}_${nodes_to_print}.csv"

# Alg 1
./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 1 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times}
#~ ./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 1 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} > "trace_greedyminstorage_${reliability_threshold}_${nodes_to_print}.csv"

# Alg least_used_node
./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 10 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times}
#~ ./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 1 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} > "trace_least_used_node_${reliability_threshold}_${nodes_to_print}.csv"

#~ # Optimal algorithm
./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 9 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times}

# HDFS 3 rep
# ./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 3 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times}
#~ # ./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 3 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} > "trace_hdfs3replications_${reliability_threshold}_${nodes_to_print}.csv"

#~ # HDFS RS
./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 6 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} 3 2
#~ ./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 6 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} 3 2 > "trace_hdfs32_${reliability_threshold}_${nodes_to_print}.csv"

#~ # Gluster FS
./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 7 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} 6 4
#~ ./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 7 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} 6 4 > "trace_glusterfs64_${reliability_threshold}_${nodes_to_print}.csv"
#~ # ./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 7 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} 0 0

# HDFS RS
./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 6 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} 6 3
#~ ./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 6 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} 6 3 > "trace_hdfs63_${reliability_threshold}_${nodes_to_print}.csv"
#~ # ./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 6 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} 0 0


#~ # Daos
./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 8 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} 1 0
#~ ./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 8 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} 1 0 > "trace_daos_${reliability_threshold}_${nodes_to_print}.csv"
# ./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition)) 8 ${add_data_pattern} $((remove_node_pattern)) $((fixed_random_seed)) $((max_N)) ${input_nodes_failure_times} 2 0


# Plotting results
python3 plot/mininet/plot.py ${data_duration_on_system} ${reliability_threshold} "drex_only" "individual" ${input_nodes} ${input_data} $((number_of_repetition)) $((max_N)) $((remove_node_pattern))
