#!/bin/bash -l

#$ -l h_rt=3:00:00
#$ -N gromacs_manual_build
#$ -pe mpi 80
#$ -cwd

export OMP_NUM_THREADS=1

module load fftw/3.3.9/gnu-10.2.0

mpiexec -np 80 /home/ccaecai/Scratch/gromacs-manual-build/gromacs-2024.4/build/bin/gmx_mpi_d mdrun -noconfout -dlb yes -s gromacs_1400k_atoms.tpr