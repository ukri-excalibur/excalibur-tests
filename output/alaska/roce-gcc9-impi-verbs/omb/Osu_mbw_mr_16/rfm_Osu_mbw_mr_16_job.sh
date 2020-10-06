#!/bin/bash
#SBATCH --job-name="rfm_Osu_mbw_mr_16_job"
#SBATCH --ntasks=16
#SBATCH --ntasks-per-node=8
#SBATCH --output=rfm_Osu_mbw_mr_16_job.out
#SBATCH --error=rfm_Osu_mbw_mr_16_job.err
#SBATCH --time=0:15:0
#SBATCH --exclusive
module load gcc/9.3.0-5abm3xg
module load intel-mpi/2019.7.217-bzs5ocr
export FI_VERBS_IFACE=p3p2
module load osu-micro-benchmarks/5.6.2-ppxiddg
mpirun -np 16 osu_mbw_mr
