# bash test/run_experiments_drex_only.sh input_nodes input_data (or number of data and their size)

# Examples
# bash test/run_experiments_drex_only.sh drex/inputs/nodes/10_most_reliable_nodes.csv drex/inputs/data/MEVA2.csv
# bash test/run_experiments_drex_only.sh drex/inputs/nodes/10_most_reliable_nodes.csv 10 1000

# Options for input nodes:
#   drex/inputs/nodes/10_most_reliable_nodes.csv
#   drex/inputs/nodes/10_most_unreliable_nodes.csv
#   drex/inputs/nodes/10_most_used_nodes.csv
#   drex/inputs/nodes/all_nodes_backblaze.csv
#   drex/inputs/nodes/most_used_node_x10.csv

# Options for input data:
#   drex/inputs/data/MEVA2.csv
#   drex/inputs/data/MEVA1.csv
#   drex/inputs/data/FB-2009_samples_24_times_1hr_0_withInputPaths.csv
#   drex/inputs/data/FB-2010_samples_24_times_1hr_0_withInputPaths.csv
#   drex/inputs/data/FB-2009_samples_24_times_1hr_1_withInputPaths.csv
#   drex/inputs/data/IBM.csv
#   drex/inputs/data/processed_sentinal-2.csv
# Or a number of data and their size like
#   100 1000
#   1000 1000

# Function to count lines in file
count_lines() {
    local filename="$1"
    local total_lines=$(wc -l < "$filename")
    local number_of_lines=$((total_lines - 1))
    echo $number_of_lines
}

python3 -m venv venv
. venv/bin/activate
#~ pip install seaborn

# Truncate current output files and add header
truncate -s 0 output_drex_only.csv
echo "algorithm,total_scheduling_time,total_storage_used,total_upload_time,total_parralelized_upload_time,number_of_data_stored,total_N,mean_storage_used,mean_upload_time,mean_N,initial_node_sizes,final_node_sizes" > output_drex_only.csv

# Storage nodes
input_nodes=$1

# Input data
if [[ "$2" == *.csv ]]; then
    input_data=$2
    echo "Input nodes: $input_nodes / Input data: $input_data"
else
    number_of_data=$2
    data_size=$3
    echo "Input nodes: $input_nodes / Input data: $number_of_data data of size $data_size"
fi


#~ for alg in alg1 alg4; do
for alg in alg1 alg2 alg3 alg4 random hdfs_three_replications; do
#~ for alg in alg1 alg2 alg3 alg4 alg2_rc alg3_rc alg4_rc random hdfs_three_replications; do
    if [[ "$2" == *.csv ]]; then
        python3 test/test-1-algorithm.py ${alg} ${input_nodes} "real_data" ${input_data}
    else
        python3 test/test-1-algorithm.py ${alg} ${input_nodes} "fixed_data" $((number_of_data)) $((data_size))
    fi
done

#~ pairs="3 2 6 3 10 4"
pairs="3 2 6 3"
pairs_array=($pairs)
for alg in hdfsrs; do
#~ for alg in hdfsrs vandermonders; do
    for ((i=0; i<${#pairs_array[@]}; i+=2)); do
        RS1=${pairs_array[i]}
        RS2=${pairs_array[i+1]}
        if [[ "$2" == *.csv ]]; then
            python3 test/test-1-algorithm.py ${alg} $((RS1)) $((RS2)) ${input_nodes} "real_data" ${input_data}
        else
            python3 test/test-1-algorithm.py ${alg} $((RS1)) $((RS2)) ${input_nodes} "fixed_data" $((number_of_data)) $((data_size))
        fi
    done
done
# pairs="6 4 11 8 12 8" # Commented cause I dont test with more than 10 nodes for now so it would not work
pairs="6 4"
pairs_array=($pairs)
for alg in glusterfs; do
    for ((i=0; i<${#pairs_array[@]}; i+=2)); do
        N=${pairs_array[i]}
        K=${pairs_array[i+1]}
        if [[ "$2" == *.csv ]]; then
            python3 test/test-1-algorithm.py ${alg} $((N)) $((K)) ${input_nodes} "real_data" ${input_data}
        else
            python3 test/test-1-algorithm.py ${alg} $((N)) $((K)) ${input_nodes} "fixed_data" $((number_of_data)) $((data_size))
        fi
    done
done

# Plotting results
if [[ "$2" == *.csv ]]; then
    python3 plot/mininet/plot.py "drex_only" "individual" ${input_nodes} ${input_data}
else
    python3 plot/mininet/plot.py "drex_only" "individual" ${input_nodes} $((number_of_data)) $((data_size))
fi
# python3 plot/mininet/plot.py $((number_of_data)) $((data_size)) "drex_only" "combined" input_nodes
