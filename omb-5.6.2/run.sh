#!/usr/bin/bash
# Usage:
#  run.sh path/to/build.json
#

#set -x #echo on
set -e # die on error
run_config=$(realpath $1) # makes it cd-proof
run_dir=$(dirname $run_config)
run_label=$(basename $run_dir)
app_label=$(basename $PWD)
job_name="$app_label-$run_label"
echo "Creating job: $job_name"
build_label=$(jq -r '.build' $run_config)
build_config=$(realpath "$run_dir/../../builds/$build_label/build.json")

echo "loading modules ..."
module purge
module load $(jq -r '.modules.compiler' $build_config)
module load $(jq -r '.modules.mpi' $build_config)
module load $(jq -r '.modules.other | @sh' $build_config | tr -d "'")
module list

cd $run_dir
mpi_opts=$(jq -r '.mpirun | @sh' $run_config | tr -d "'")
cmdstr="mpirun $mpi_opts osu_bw"
sbatch_opts=$(jq -r '.sbatch | to_entries | map( "\(.key)=\(.value)") | join(" ")' $run_config)
sbatch --job-name=$job_name $sbatch_opts --wrap="$cmdstr"
