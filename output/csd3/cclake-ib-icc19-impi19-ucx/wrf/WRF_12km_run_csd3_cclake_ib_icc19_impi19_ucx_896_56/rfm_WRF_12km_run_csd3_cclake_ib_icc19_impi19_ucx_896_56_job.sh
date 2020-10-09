#!/bin/bash
#SBATCH --job-name="rfm_WRF_12km_run_csd3_cclake_ib_icc19_impi19_ucx_896_56_job"
#SBATCH --ntasks=896
#SBATCH --ntasks-per-node=56
#SBATCH --output=rfm_WRF_12km_run_csd3_cclake_ib_icc19_impi19_ucx_896_56_job.out
#SBATCH --error=rfm_WRF_12km_run_csd3_cclake_ib_icc19_impi19_ucx_896_56_job.err
#SBATCH --time=3:0:0
#SBATCH --partition=cclake
#SBATCH --account=support-cpu
#SBATCH --exclude=cpu-p-[1-280,337-672]
module load rhel7/default-ccl
export UCX_NET_DEVICES=mlx5_0:1
export WRF_DIR=$HOME/wrf-build-icc19-impi19-hsw
ln -sf $WRF_DIR/WRFV3.8.1/run/* .
ln -sf /home/hpcbras1/hpc-tests/apps/wrf/downloads/12km/* .
sed '/&dynamics/a \ use_baseparam_fr_nml = .t.' -i namelist.input
time \
srun wrf.exe
