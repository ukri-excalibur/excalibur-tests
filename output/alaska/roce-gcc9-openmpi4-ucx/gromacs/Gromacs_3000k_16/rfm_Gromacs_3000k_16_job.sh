#!/bin/bash
#SBATCH --job-name="rfm_Gromacs_3000k_16_job"
#SBATCH --ntasks=512
#SBATCH --ntasks-per-node=32
#SBATCH --output=rfm_Gromacs_3000k_16_job.out
#SBATCH --error=rfm_Gromacs_3000k_16_job.err
#SBATCH --exclusive
module load gcc/9.3.0-5abm3xg
module load openmpi/4.0.3-qpsxmnc
export SLURM_MPI_TYPE=pmix_v2
export UCX_NET_DEVICES=mlx5_1:1
module load gromacs/2016.4-y5sjbs4
time \
srun gmx_mpi mdrun -s benchmark.tpr -g 3000k-atoms.log -noconfout
