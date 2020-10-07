#!/bin/bash
#SBATCH --job-name="rfm_IMB_Uniband_0_25_job"
#SBATCH --ntasks=16
#SBATCH --ntasks-per-node=8
#SBATCH --output=rfm_IMB_Uniband_0_25_job.out
#SBATCH --error=rfm_IMB_Uniband_0_25_job.err
#SBATCH --time=0:10:0
#SBATCH --exclusive
module load gcc/9.3.0-5abm3xg
module load openmpi/4.0.3-qpsxmnc
export SLURM_MPI_TYPE=pmix_v2
export UCX_NET_DEVICES=mlx5_1:1
module load intel-mpi-benchmarks/2019.5-dwg5q6j
srun IMB-MPI1 uniband -npmin 1
