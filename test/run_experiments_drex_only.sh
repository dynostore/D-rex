# bash test/run_experiments_drex_only.sh data_duration_on_system reliability_threshold input_nodes input_data (or number of data and their size)

# Examples
# bash test/run_experiments_drex_only.sh 365 0.99 drex/inputs/nodes/10_most_used_nodes.csv drex/inputs/data/test.csv

# Options for data duration on system
#   365
#   730
#   3650

# Options for reliability threshold
#   0.9
#   0.99
#   0.999
#   0.9999
#   0.99999999999 (aws 11 nines)

# Options for input nodes:
#   drex/inputs/nodes/10_most_reliable_nodes.csv 122 TB 0.5100 AFR
#   drex/inputs/nodes/10_most_unreliable_nodes.csv 112 TB 6.4790 AFR
#   drex/inputs/nodes/10_most_used_nodes.csv 120 TB 1.2390 AFR
#   drex/inputs/nodes/all_nodes_backblaze.csv 354 TB 2.7487 AFR
#   drex/inputs/nodes/most_used_node_x10.csv 140 TB 0.9700 AFR

# Options for input data:
#   drex/inputs/data/MEVA2.csv  27 GB
#   drex/inputs/data/MEVA1.csv  459 GB
#   drex/inputs/data/MEVA_merged.csv  487 GB W 0 R

#   drex/inputs/data/FB-2009_samples_24_times_1hr_0_withInputPaths.csv  25 TB
#   drex/inputs/data/FB-2010_samples_24_times_1hr_0_withInputPaths.csv  1 PB
#   drex/inputs/data/FB-2009_samples_24_times_1hr_1_withInputPaths.csv  32 TB
#   drex/inputs/data/FB_merged  928 TB W 161 TB R

#   drex/inputs/data/IBM.csv    3 PB W 111 PB R

#   drex/inputs/data/processed_sentinal-2.csv 13 PB W

#   drex/inputs/data/all_merged.csv 18 PB W 112 PB R

# Or a number of data and their size like
#   100 1000
#   1000 1000

python3 -m venv venv
. venv/bin/activate
#~ pip install seaborn

# Truncate current output files and add header
truncate -s 0 output_drex_only.csv
echo "algorithm,total_scheduling_time,total_storage_used,total_upload_time,total_parralelized_upload_time,number_of_data_stored,total_N,mean_storage_used,mean_upload_time,mean_N,initial_node_sizes,final_node_sizes" > output_drex_only.csv

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
    echo "Input nodes: $input_nodes / Input data: $input_data"
else
    number_of_data=$4
    data_size=$5
    echo "Input nodes: $input_nodes / Input data: $number_of_data data of size $data_size"
fi

number_of_repetition=1

# Choosing our alg4 version
if [ $number_nodes -ge 1 ]; then
    alg4=alg4_rc
else
    alg4=alg4
fi

#~ # for alg in alg1 alg2 ${alg4} random hdfs_three_replications; do
#~ # for alg in alg1 ${alg4} random hdfs_three_replications; do
#~ for alg in alg1 random hdfs_three_replications; do
#~ # for alg in alg1 alg2 alg3 ${alg4} random hdfs_three_replications; do
    #~ if [[ "$4" == *.csv ]]; then
        #~ python3 test/test-1-algorithm.py ${alg} ${data_duration_on_system} ${reliability_threshold} ${input_nodes} "real_data" ${input_data}
    #~ else
        #~ python3 test/test-1-algorithm.py ${alg} ${data_duration_on_system} ${reliability_threshold} ${input_nodes} "fixed_data" $((number_of_data)) $((data_size))
    #~ fi
#~ done

#~ pairs="3 2 6 3"
#~ # pairs="3 2 6 3 10 4"
#~ pairs_array=($pairs)
#~ for alg in hdfsrs; do
#~ # for alg in hdfsrs vandermonders; do
    #~ for ((i=0; i<${#pairs_array[@]}; i+=2)); do
        #~ RS1=${pairs_array[i]}
        #~ RS2=${pairs_array[i+1]}
        #~ if [[ "$4" == *.csv ]]; then
            #~ python3 test/test-1-algorithm.py ${alg} ${data_duration_on_system} ${reliability_threshold} $((RS1)) $((RS2)) ${input_nodes} "real_data" ${input_data}
        #~ else
            #~ python3 test/test-1-algorithm.py ${alg} ${data_duration_on_system} ${reliability_threshold} $((RS1)) $((RS2)) ${input_nodes} "fixed_data" $((number_of_data)) $((data_size))
        #~ fi
    #~ done
#~ done

#~ pairs="6 4"
#~ # pairs="6 4 11 8 12 8" # Commented cause I dont test with more than 10 nodes for now so it would not work
#~ pairs_array=($pairs)
#~ for alg in glusterfs; do
    #~ for ((i=0; i<${#pairs_array[@]}; i+=2)); do
        #~ N=${pairs_array[i]}
        #~ K=${pairs_array[i+1]}
        #~ if [[ "$4" == *.csv ]]; then
            #~ python3 test/test-1-algorithm.py ${alg} ${data_duration_on_system} ${reliability_threshold} $((N)) $((K)) ${input_nodes} "real_data" ${input_data}
        #~ else
            #~ python3 test/test-1-algorithm.py ${alg} ${data_duration_on_system} ${reliability_threshold} $((N)) $((K)) ${input_nodes} "fixed_data" $((number_of_data)) $((data_size))
        #~ fi
    #~ done
#~ done

gcc -Wall drex/schedulers/algorithm4.c -o alg4 -lm
./alg4 ${input_nodes} ${input_data} ${data_duration_on_system} ${reliability_threshold} $((number_of_repetition))

# Plotting results
if [[ "$4" == *.csv ]]; then
    python3 plot/mininet/plot.py ${data_duration_on_system} ${reliability_threshold} "drex_only" "individual" ${input_nodes} ${input_data}
else
    python3 plot/mininet/plot.py ${data_duration_on_system} ${reliability_threshold} "drex_only" "individual" ${input_nodes} $((number_of_data)) $((data_size))
fi
#~ # python3 plot/mininet/plot.py $((number_of_data)) $((data_size)) "drex_only" "combined" input_nodes
