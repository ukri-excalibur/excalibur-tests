#!/usr/bin/bash
# Clear or refresh all jupyter notebooks found in apps/
# Usage:
#    plot.sh [refresh | clear]
#
# Without any argyments it will list notebooks found.

notebooks=$(find apps/ -name *.ipynb '!' -name *checkpoint*)
for nb in $notebooks; do
    if [ "$1" == "" ]; then
        echo $nb
    elif [ "$1" == "refresh" ]; then
        jupyter nbconvert --to notebook --execute --inplace $nb
    elif [ "$1" == "clear" ]; then
        jupyter nbconvert --clear-output --inplace $nb
    fi
done

#