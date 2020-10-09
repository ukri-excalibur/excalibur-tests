#!/bin/bash
#SBATCH --job-name="rfm_WRF_2_5km_run_csd3_cclake_roce_icc19_impi19_ucx_1792_56_job"
#SBATCH --ntasks=1792
#SBATCH --ntasks-per-node=56
#SBATCH --output=rfm_WRF_2_5km_run_csd3_cclake_roce_icc19_impi19_ucx_1792_56_job.out
#SBATCH --error=rfm_WRF_2_5km_run_csd3_cclake_roce_icc19_impi19_ucx_1792_56_job.err
#SBATCH --time=3:0:0
#SBATCH --partition=cclake
#SBATCH --account=support-cpu
#SBATCH --exclude=cpu-p-[1-280,337-672]
module load rhel7/default-ccl
export UCX_NET_DEVICES=mlx5_1:1
export WRF_DIR=$HOME/wrf-build-icc19-impi19-hsw/WRFV3.8.1
ln -sf $WRF_DIR/run/* .
ln -sf /home/hpcbras1/hpc-tests/apps/wrf/downloads/2.5km/* .
cat rst_6hr* | gunzip -c > wrfrst_d01_2005-06-04_06_00_00
gunzip --force wrfbdy_d01.gz
sed -i '/&dynamics/a \ use_baseparam_fr_nml = .t.' namelist.input
sed -E -i 's/( io_form_[[:alpha:]]+ += )11,/\12,/' namelist.input
time \
srun wrf.exe
