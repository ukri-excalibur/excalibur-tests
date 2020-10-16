#!/bin/bash
#SBATCH --job-name="rfm_Openfoam_Mbike_csd3_cclake_ib_gcc9_ompi3_ucx_1792_56_job"
#SBATCH --ntasks=1792
#SBATCH --ntasks-per-node=56
#SBATCH --output=rfm_Openfoam_Mbike_csd3_cclake_ib_gcc9_ompi3_ucx_1792_56_job.out
#SBATCH --error=rfm_Openfoam_Mbike_csd3_cclake_ib_gcc9_ompi3_ucx_1792_56_job.err
#SBATCH --time=1:0:0
#SBATCH --exclusive
#SBATCH --partition=cclake
#SBATCH --account=support-cpu
#SBATCH --exclude=cpu-p-[1-280,337-672]
module load openmpi-3.1.6-gcc-9.1.0-omffmfv
export SLURM_MPI_TYPE=pmix_v3
export UCX_NET_DEVICES=mlx5_0:1
module load openfoam-org-7-gcc-9.1.0-dahapws
tar --strip-components 2 -xf Motorbike_bench_template.tar.gz bench_template/basecase
./Allclean
sed -i -- "s/method .*/method          scotch;/g" system/decomposeParDict
sed -i -- "s/numberOfSubdomains .*/numberOfSubdomains 1792;/g" system/decomposeParDict
sed -i -- 's/    #include "streamLines"//g' system/controlDict
sed -i -- 's/    #include "wallBoundedStreamLines"//g' system/controlDict
sed -i -- 's|caseDicts|caseDicts/mesh/generation|' system/meshQualityDict
./Allmesh
time \
srun simpleFoam -parallel
