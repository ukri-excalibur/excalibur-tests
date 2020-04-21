#!/usr/bin/bash
#SBATCH -N 2
#SBATCH -n 2
module purge
module load gnu8/8.3.0 openmpi3/3.1.4 omb
mpirun --mca btl_base_warn_component_unused 0 osu_bw

