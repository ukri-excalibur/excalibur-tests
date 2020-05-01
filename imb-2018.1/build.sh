#!/usr/bin/bash
# Usage:
#  build.sh path/to/build.json
#

#set -x #echo on
set -e # die on error

CONFIG=$(realpath $1) # makes it cd-proof
VER=$(jq -r '.version' $CONFIG)
CONF_DIR="$(dirname $1)"

# check we have modules available - have to do a load otherwise can't check dependencies
module purge
module load $(jq -r '.modules.compiler' $CONFIG)
module load $(jq -r '.modules.mpi' $CONFIG)
module load $(jq -r '.modules.other | @sh' $CONFIG | tr -d "'")

# if so, then nothing to do:
echo "imb $VER installed with module, nothing to do."
