#!/usr/bin/bash
# Clear or refresh jupyter notebooks found in apps/
# Usage:
#
# List all notebooks:
#   plot.sh
# Refresh or clear all or specified notebooks:
#   plot.sh [refresh | clear] [notebookpath ...]

if [ "$#" -gt 1 ]; then
    cmd=$1
    shift
    notebooks=$@
elif [ "$#" -eq 1 ]; then
    cmd=$1
    notebooks=$(find apps/ -name *.ipynb '!' -name *checkpoint*)
elif [ "$#" -eq 0 ]; then
    cmd=echo
    notebooks=$(find apps/ -name *.ipynb '!' -name *checkpoint*)
fi

if [ "$cmd" == "refresh" ]; then
    cmd="jupyter nbconvert --to notebook --execute --inplace"
elif [ "$cmd" == "clear" ]; then
    cmd="jupyter nbconvert --clear-output --inplace --ClearOutputPreprocessor.enabled=True"
else
    cmd="echo"
fi

for nb in $notebooks; do
    $cmd $nb
done