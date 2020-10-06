#!/bin/bash
#SBATCH --job-name="rfm_Osu_alltoall_job"
#SBATCH --ntasks=64
#SBATCH --ntasks-per-node=32
#SBATCH --output=rfm_Osu_alltoall_job.out
#SBATCH --error=rfm_Osu_alltoall_job.err
#SBATCH --time=0:10:0
#SBATCH --exclusive
module load gcc/9.3.0-5abm3xg
module load intel-mpi/2019.7.217-bzs5ocr
export FI_VERBS_IFACE=p3p2
module load osu-micro-benchmarks/5.6.2-ppxiddg
mpirun -np 64 osu_alltoall
