#!/bin/bash

#$ -pe smp 12     # Specify parallel environment and legal core size
#$ -q hpc@@colon       # Specify queue
#$ -N sub_7       # Specify job name

module load lammps     # Required modules

mpirun -np $NSLOTS lmp_mpi -in modified_input_7.in  # Application to execute

                  
