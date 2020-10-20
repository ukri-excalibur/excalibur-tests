#!/bin/bash
#SBATCH --job-name="rfm_IntelHpl_single_job"
#SBATCH --ntasks=1
#SBATCH --ntasks-per-node=1
#SBATCH --output=rfm_IntelHpl_single_job.out
#SBATCH --error=rfm_IntelHpl_single_job.err
#SBATCH --time=1:0:0
#SBATCH --exclusive
#SBATCH --partition=cclake
#SBATCH --account=support-cpu
#SBATCH --exclude=cpu-p-[1-280,337-672]
module load rhel7/default-ccl
export UCX_NET_DEVICES=mlx5_0:1
export PATH=$PATH:$MKLROOT/benchmarks/mp_linpack/
srun xhpl_intel64_dynamic
