#!/bin/bash
#SBATCH --job-name="rfm_Castep_TiN_job"
#SBATCH --ntasks=8
#SBATCH --ntasks-per-node=8
#SBATCH --output=rfm_Castep_TiN_job.out
#SBATCH --error=rfm_Castep_TiN_job.err
#SBATCH --time=1:0:0
#SBATCH --exclusive
#SBATCH --partition=cclake
#SBATCH --account=support-cpu
#SBATCH --exclude=cpu-p-[1-168,225-672]
module load rhel7/default-ccl
export UCX_NET_DEVICES=mlx5_1:1
module load castep
tar --strip-components=1 -xf TiN.tgz
time \
srun castep TiN-mp
