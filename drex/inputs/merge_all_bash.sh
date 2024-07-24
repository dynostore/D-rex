#!/bin/bash

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 output_file input_file1 input_file2 ... input_fileN"
  exit 1
fi

output_file="$1"
shift

# Get the header from the first file and write it to the output file
head -n 1 "$1" > "$output_file"

# Append the contents of each file to the output file, skipping the header for all but the first file
for input_file in "$@"; do
  tail -n +2 "$input_file" >> "$output_file"
done
