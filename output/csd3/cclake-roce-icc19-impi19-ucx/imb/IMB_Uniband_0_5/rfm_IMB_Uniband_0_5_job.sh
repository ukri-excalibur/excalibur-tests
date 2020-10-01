#!/bin/bash
#SBATCH --job-name="rfm_IMB_Uniband_0_5_job"
#SBATCH --ntasks=56
#SBATCH --ntasks-per-node=28
#SBATCH --output=rfm_IMB_Uniband_0_5_job.out
#SBATCH --error=rfm_IMB_Uniband_0_5_job.err
#SBATCH --time=0:10:0
#SBATCH --exclusive
#SBATCH --partition=cclake
#SBATCH --account=support-cpu
#SBATCH --exclude=cpu-p-[1-280,337-672]
module load rhel7/default-ccl
export UCX_NET_DEVICES=mlx5_1:1
srun IMB-MPI1 uniband -npmin 1
