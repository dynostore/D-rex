# Code used to parse the data from https://github.com/SWIMProjectUCB/SWIM/wiki/Workloads-repository
# python3 drex/inputs/parsing_code/parse_SWIM_map_reduce.py drex/inputs/data/raw/FB-2009_samples_24_times_1hr_0.tsv drex/inputs/data/raw/FB-2009_samples_24_times_1hr_1.tsv drex/inputs/data/raw/FB-2010_samples_24_times_1hr_0.tsv drex/inputs/data/FB-2009_samples_24_times_1hr_0.json

import json
import sys

def parse_input_file(input_file_1, input_file_2, input_file_3, number_of_input_file):
    data_list = []
    total_number_of_jobs = 0
    last_submit_time = 0
    submit_time_to_add = 0
    for i in range (0, number_of_input_file):
        if i == 0:
            current_input_file = input_file_1
        elif i == 1:
            last_submit_time = submit_time_to_add
            current_input_file = input_file_2
        else:
            last_submit_time = submit_time_to_add
            current_input_file = input_file_3
        print("Reading", current_input_file)
        with open(current_input_file, 'r') as f:
            for line in f:
                fields = line.strip().split('\t')
                # ~ job_id = int(fields[0].replace('job', ''))
                job_id = total_number_of_jobs
                submit_time = int(fields[1]) + last_submit_time
                submit_time_to_add = submit_time
                size = sum(map(int, fields[3:]))/1000000 # Divided cause we want megabytes
                if size < 1:
                    size = 1
                data_list.append({
                    "id": job_id,
                    "size": size,
                    "submit_time": submit_time,
                    "time_spent": "0"
                })
                total_number_of_jobs += 1
    print("There are", total_number_of_jobs, "data")
    return data_list

def write_to_json(data_list, output_file):
    with open(output_file, 'w') as f:
        json.dump({"data_list": data_list}, f, indent=2)

def main(input_file_1, input_file_2, input_file_3, output_file):
    number_of_input_file = 3
    data_list = parse_input_file(input_file_1, input_file_2, input_file_3, number_of_input_file)
    write_to_json(data_list, output_file)

if __name__ == "__main__":
    input_file_1 = sys.argv[1]
    input_file_2 = sys.argv[2]
    input_file_3 = sys.argv[3]
    output_file = sys.argv[4]
    main(input_file_1, input_file_2, input_file_3, output_file)

