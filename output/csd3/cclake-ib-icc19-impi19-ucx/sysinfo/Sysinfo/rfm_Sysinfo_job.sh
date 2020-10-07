#!/bin/bash
#SBATCH --job-name="rfm_Sysinfo_job"
#SBATCH --ntasks=56
#SBATCH --ntasks-per-node=1
#SBATCH --output=rfm_Sysinfo_job.out
#SBATCH --error=rfm_Sysinfo_job.err
#SBATCH --time=0:10:0
#SBATCH --partition=cclake
#SBATCH --account=support-cpu
#SBATCH --exclude=cpu-p-[1-280,337-672]
module load rhel7/default-ccl
export UCX_NET_DEVICES=mlx5_0:1
srun python sysinfo.py
echo Done
