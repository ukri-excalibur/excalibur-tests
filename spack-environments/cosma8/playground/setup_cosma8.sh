#!/bin/bash
set -euo pipefail
ENVDIR=../spack-environments/cosma8
COMBINATIONS=all_combinations.txt
rm -r $ENVDIR
spack env create -d $ENVDIR
spack env activate -d $ENVDIR
while read compiler mpi tofind
do
( 
module load $compiler $mpi &> /dev/null
echo $compiler $mpi
spack compiler find
spack external find  
) 
done < $COMBINATIONS 
