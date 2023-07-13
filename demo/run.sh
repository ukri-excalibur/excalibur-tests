#!/bin/bash

app=$1
spec=$2
system=$3

apps_dir=excalibur-tests/benchmarks/apps

if [ $system == archer2 ]
then
    reframe -c $apps_dir/$app -r -J'--qos=short' --system archer2 -S spack_spec=$spec
elif [ $system == cosma ]
then
    reframe -c $apps_dir/$app -r -J'--account=do006' --system cosma8 -S spack_spec=$spec
elif [ $system == csd3 ]
then
    reframe -c $apps_dir/$app -r -J'--account=DIRAC-DO006-CPU' --system csd3-skylake -S spack_spec=$spec
elif [ $system == isambard ]
then
    reframe -c $apps_dir/$app -r --system isambard-macs:cascadelake -S build_locally=false -S spack_spec=$spec
fi
