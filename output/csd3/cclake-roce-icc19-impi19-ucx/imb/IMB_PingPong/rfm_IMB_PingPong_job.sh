#!/bin/bash
#SBATCH --job-name="rfm_IMB_PingPong_job"
#SBATCH --ntasks=2
#SBATCH --ntasks-per-node=1
#SBATCH --output=rfm_IMB_PingPong_job.out
#SBATCH --error=rfm_IMB_PingPong_job.err
#SBATCH --time=0:10:0
#SBATCH --exclusive
#SBATCH --partition=cclake
#SBATCH --account=support-cpu
#SBATCH --exclude=cpu-p-[1-280,337-672]
module load rhel7/default-ccl
export UCX_NET_DEVICES=mlx5_1:1
srun IMB-MPI1 pingpong
