#!/bin/bash

# ----------------------------------------------------------
# Source of Instructions: https://ambermd.org/tutorials/advanced/tutorial15/Tutorial2.php
# Amber Tutorial: Simulations of a room-temperature ionic liquid. By Chris Lim and David A Case
# Followed till step 5 - Generating the coordinate and topology files. Then used the amb2gro_top_gro.py tool to convert amber files to gromacs files.
# ----------------------------------------------------------

# Check if the correct number of arguments is provided
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 res_name charge"
    exit 1
fi

# Assign inputs to variables
res_name=$1
charge=$2

# Load amber and ambertools
module load amber

# Start by creating directories for each of the residues you want to parametrize using GAFF
res_folder=${res_name}-Amber
mkdir ${res_folder}

# Copy the raw pdb files into the new directory
cp pdb-files/${res_name}.pdb ${res_folder}

cd ${res_folder}

# Clean pdb file to remove unnecessary fields
pdb4amber -i ${res_name}.pdb -o ${res_name}_cleaned.pdb

# Generate mol2 file
antechamber -i ${res_name}_cleaned.pdb -fi pdb -o ${res_name}.mol2 -fo mol2 -c bcc -nc ${charge}

# This is where you would edit charges in the mol2 file if necessary

# Generate FF modification files if necessary (will be mostly empty if not needed)
parmchk2 -i ${res_name}.mol2 -f mol2 -o frcmod.${res_name}

# Back to parent folder
cd ..
