#!/bin/bash
#SBATCH --job-name="rfm_Hpl_single_job"
#SBATCH --ntasks=32
#SBATCH --ntasks-per-node=32
#SBATCH --output=rfm_Hpl_single_job.out
#SBATCH --error=rfm_Hpl_single_job.err
#SBATCH --exclusive
module load gcc/9.3.0-5abm3xg
module load openmpi/4.0.3-qpsxmnc
export SLURM_MPI_TYPE=pmix_v2
export UCX_NET_DEVICES=mlx5_1:1
module load hpl/2.3-iyor3px
srun xhpl
