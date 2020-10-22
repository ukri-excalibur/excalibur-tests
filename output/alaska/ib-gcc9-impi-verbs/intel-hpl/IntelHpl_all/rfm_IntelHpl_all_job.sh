#!/bin/bash
#SBATCH --job-name="rfm_IntelHpl_all_job"
#SBATCH --ntasks=16
#SBATCH --ntasks-per-node=1
#SBATCH --output=rfm_IntelHpl_all_job.out
#SBATCH --error=rfm_IntelHpl_all_job.err
#SBATCH --time=1:0:0
#SBATCH --exclusive
module load gcc/9.3.0-5abm3xg
module load intel-mpi/2019.7.217-bzs5ocr
export FI_VERBS_IFACE=ib
module load intel-mkl/2020.1.217-5tpgp7b
mpirun -np 16 $MKLROOT/benchmarks/mp_linpack/xhpl_intel64_dynamic
