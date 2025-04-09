#!/bin/bash

module load amber

# Check if the correct number of arguments is provided
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 res_name charge"
    exit 1
fi

# Assign inputs to variables
res_name=$1
charge=$2

# Enter folder containing residue.mol2 files
res_folder=${res_name}-Amber
cd ${res_folder}

# ## Needs Debugging
# # Create template of force field modification files
# amber2lt.py --in frcmod.${res_name} --name ${res_name}_ForceField > ${res_name}_force_field.lt

# # Convert mol2 files to lt files using the modified force field  files
# mol22lt.py --in ${res_name}.mol2 --out ${res_name}.lt --name ${res_name} --ff ${res_name}_ForceField --ff-file ${res_name}_force_field.lt

# Convert mol2 files to lt files using GAFF2 force field
mol22lt.py --in ${res_name}.mol2 --out ${res_name}.lt --name ${res_name} --ff GAFF2 --ff-file gaff2.lt
# Convert mol2 files to lt files using OPLS-AA force field
#mol22lt.py --in ${res_name}.mol2 --out ${res_name}.lt --name ${res_name} --ff OPLSAA --ff-file oplsaa.lt

# Save the lt files in the parent folder
cp *.lt ../
cd ..
