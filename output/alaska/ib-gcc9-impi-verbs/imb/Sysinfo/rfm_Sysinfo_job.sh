#!/bin/bash
#SBATCH --job-name="rfm_Sysinfo_job"
#SBATCH --ntasks=16
#SBATCH --ntasks-per-node=1
#SBATCH --output=rfm_Sysinfo_job.out
#SBATCH --error=rfm_Sysinfo_job.err
#SBATCH --time=0:10:0
module load gcc/9.3.0-5abm3xg
module load intel-mpi/2019.7.217-bzs5ocr
export FI_VERBS_IFACE=ib
module load intel-mpi-benchmarks/2019.5-w54huiw
mpirun -np 16 python sysinfo.py
echo Done
cat *.info > all.info
