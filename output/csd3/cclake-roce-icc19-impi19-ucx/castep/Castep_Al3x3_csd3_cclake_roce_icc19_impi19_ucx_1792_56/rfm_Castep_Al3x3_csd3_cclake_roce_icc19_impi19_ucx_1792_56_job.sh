#!/bin/bash
#SBATCH --job-name="rfm_Castep_Al3x3_csd3_cclake_roce_icc19_impi19_ucx_1792_56_job"
#SBATCH --ntasks=1792
#SBATCH --ntasks-per-node=56
#SBATCH --output=rfm_Castep_Al3x3_csd3_cclake_roce_icc19_impi19_ucx_1792_56_job.out
#SBATCH --error=rfm_Castep_Al3x3_csd3_cclake_roce_icc19_impi19_ucx_1792_56_job.err
#SBATCH --time=2:0:0
#SBATCH --exclusive
#SBATCH --partition=cclake
#SBATCH --account=support-cpu
#SBATCH --exclude=cpu-p-[1-168,225-672]
module load rhel7/default-ccl
export UCX_NET_DEVICES=mlx5_1:1
module load castep
tar --strip-components=2 -xf Al3x3.tgz
time \
srun castep al3x3
