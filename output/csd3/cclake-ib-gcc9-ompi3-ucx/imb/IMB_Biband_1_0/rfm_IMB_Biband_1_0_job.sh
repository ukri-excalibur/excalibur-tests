#!/bin/bash
#SBATCH --job-name="rfm_IMB_Biband_1_0_job"
#SBATCH --ntasks=112
#SBATCH --ntasks-per-node=56
#SBATCH --output=rfm_IMB_Biband_1_0_job.out
#SBATCH --error=rfm_IMB_Biband_1_0_job.err
#SBATCH --time=0:10:0
#SBATCH --exclusive
#SBATCH --partition=cclake
#SBATCH --account=support-cpu
#SBATCH --exclude=cpu-p-[1-280,337-672]
module load openmpi-3.1.6-gcc-9.1.0-omffmfv
export SLURM_MPI_TYPE=pmix_v3
export UCX_NET_DEVICES=mlx5_0:1
module load intel-mpi-benchmarks-2019.6-gcc-9.1.0-5tbknir
srun IMB-MPI1 biband -npmin 1
