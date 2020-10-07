#!/bin/bash
#SBATCH --job-name="rfm_WRF_download_job"
#SBATCH --ntasks=1
#SBATCH --output=rfm_WRF_download_job.out
#SBATCH --error=rfm_WRF_download_job.err
#SBATCH --time=1:0:0
#SBATCH --partition=cclake
#SBATCH --account=support-cpu
#SBATCH --exclude=cpu-p-[1-280,337-672]
module load rhel7/default-ccl
export UCX_NET_DEVICES=mlx5_0:1
export WRF_DIR=$HOME/wrf-build-icc19-impi19-hsw
srun echo Done.
