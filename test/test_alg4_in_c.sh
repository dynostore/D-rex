truncate -s 0 output_drex_only.csv
gcc -Wall drex/schedulers/algorithm4.c -o alg4 -lm
#~ gcc -DPRINT -Wall drex/schedulers/algorithm4.c -o alg4 -lm
./alg4 drex/inputs/nodes/10_most_reliable_nodes.csv drex/inputs/data/test.csv 365 0.99 2
#~ ./alg4 drex/inputs/nodes/10_most_reliable_nodes.csv drex/inputs/data/MEVA_merged.csv 365 0.99 3
cat output_drex_only.csv
