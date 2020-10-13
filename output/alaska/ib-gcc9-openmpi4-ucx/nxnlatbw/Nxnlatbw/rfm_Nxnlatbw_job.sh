#!/bin/bash
#SBATCH --job-name="rfm_Nxnlatbw_job"
#SBATCH --ntasks=16
#SBATCH --ntasks-per-node=1
#SBATCH --output=rfm_Nxnlatbw_job.out
#SBATCH --error=rfm_Nxnlatbw_job.err
#SBATCH --time=1:0:0
#SBATCH --exclusive
module load gcc/9.3.0-5abm3xg
module load openmpi/4.0.3-qpsxmnc
export SLURM_MPI_TYPE=pmix_v2
export UCX_NET_DEVICES=mlx5_0:1
srun nxnlatbw
