# bash test/run_experiments_drex_only.sh

python3 -m venv venv  
. venv/bin/activate

# Truncate current output files and add header
truncate -s 0 output_drex_only.csv
echo "Algorithm, Total Scheduling Time (seconds), Total Storage Used (megabytes), Total Upload Time (seconds), Total Parallelized Upload Time (seconds)" > output.txt

# Parameters
number_of_data=10
data_size=200 # In MB
input_nodes="drex/inputs/nodes/10_most_used_nodes.csv"
#~ input_data="drex/inputs/data/test.txt"

# Loop over execution
for alg in alg1 alg2 alg3 alg4 alg2_rc alg3_rc alg4_rc random hdfs_three_replications; do
    python3 test/test-1-algorithm.py ${alg} ${input_nodes} "fixed_data" $((number_of_data)) $((data_size))
    #~ python3 test/test-1-algorithm.py ${alg} ${input_nodes} "real_data" ${input_data}
done
#~ pairs="3 2 6 3 10 4"
#~ pairs_array=($pairs)
#~ for alg in hdfsrs vandermonders; do
    #~ for ((i=0; i<${#pairs_array[@]}; i+=2)); do
        #~ RS1=${pairs_array[i]}
        #~ RS2=${pairs_array[i+1]}
        #~ python3 test/test-1-algorithm.py ${alg} $((RS1)) $((RS2)) ${input_nodes} "fixed_data" $((number_of_data)) $((data_size))
    #~ done
#~ done
#~ # pairs="6 4 11 8 12 8" # Commented cause I don't test with more than 10 nodes for now so it would not work
#~ pairs="6 4"
#~ pairs_array=($pairs)
#~ for alg in glusterfs; do
    #~ for ((i=0; i<${#pairs_array[@]}; i+=2)); do
        #~ N=${pairs_array[i]}
        #~ K=${pairs_array[i+1]}
        #~ python3 test/test-1-algorithm.py ${alg} $((N)) $((K)) ${input_nodes} "fixed_data" $((number_of_data)) $((data_size))
    #~ done
#~ done