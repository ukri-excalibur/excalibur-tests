#!/bin/bash

app=$1
system=$2

if [ $system == archer2 ]
then
    reframe -c benchmarks/apps/$app -r -J'--qos=short' --system archer2
elif [ $system == cosma ]
then
    reframe -c benchmarks/apps/$app -r -J'--account=do006' --system cosma8
elif [ $system == csd3 ]
then
    reframe -c benchmarks/apps/$app -r -J'--account=do006' --system csd3-skylake
elif [ $system == isambard ]
then
    reframe -c benchmarks/apps/$app -r --system isambard-macs:cascadelake -S build_locally=false
fi
