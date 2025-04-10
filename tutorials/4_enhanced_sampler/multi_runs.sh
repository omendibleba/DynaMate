#!/bin/bash

# Define counter
n=0

# Loop through each umbrella_* directory in natural order
for dir in $(ls -d umbrella_* | sort -V); do
    # Check if it is a directory
    if [ -d "$dir" ]; then
        # Enter the directory
        cd "$dir"
        
        # Check if the input file exists
        input_file="sub_${n}.sh"
        # input_file="modified_input_${n}.in"
        #echo "Checking $input_file in $dir"
        if [ -f "$input_file" ]; then
            # Run the command
            #lmp -in "$input_file"
            qsub "$input_file"
        else
            echo "Error: $input_file not found in $dir"
            # Optionally, you could exit the script here
            # exit 1
        fi
                
        # Go back to the parent directory
        cd ..

        # Increment the counter
        n=$((n+1))
    else
        echo "Error: Directory $dir not found"
    fi
done
