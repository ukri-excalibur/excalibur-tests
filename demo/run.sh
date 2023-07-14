#!/bin/bash

app=$1
compiler=$2
system=$3
spec=$app\%$compiler

apps_dir=excalibur-tests/benchmarks/apps

if [ $system == archer2 ]
then
    reframe -c $apps_dir/$app -r -J'--qos=short' --system archer2 -S spack_spec=$spec --setvar=num_cpus_per_task=8  --setvar=num_tasks_per_node=2 --setvar=num_tasks=8
elif [ $system == cosma ]
then
    reframe -c $apps_dir/$app -r -J'--account=do006' --system cosma8 -S spack_spec=$spec --setvar=num_cpus_per_task=8  --setvar=num_tasks_per_node=2 --setvar=num_tasks=8
elif [ $system == csd3 ]
then
    reframe -c $apps_dir/$app -r -J'--account=DIRAC-DO006-CPU' --system csd3-cascadelake -S spack_spec=$spec --setvar=num_cpus_per_task=8  --setvar=num_tasks_per_node=2 --setvar=num_tasks=8
elif [ $system == isambard ]
then
    reframe -c $apps_dir/$app -r --system isambard-macs:cascadelake -S build_locally=false -S spack_spec=$spec --setvar=num_cpus_per_task=8  --setvar=num_tasks_per_node=2 --setvar=num_tasks=8
fi
