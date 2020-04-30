#!/usr/bin/bash
#set -x #echo on

# NB: DCMAKE_INSTALL_PREFIX as this is relative to where this script moves to

CONFIG=$(<$1)
GROMACS_VER=$(jq -r '.version' <<< $CONFIG)
TAR_NAME="gromacs-${GROMACS_VER}.tar.gz"
UNTAR_DIR="gromacs-${GROMACS_VER}" # assumption about tar structure!
DOWNLOAD_PATH="http://ftp.gromacs.org/pub/gromacs/${TAR_NAME}"
BUILD_DIR=$(dirname $1)
echo "Will build v$GROMACS_VER in $BUILD_DIR"

# start in the pwd, i.e. hpc-tests/gromacs:
echo "downloading and unpacking ..."
if [ ! -f $TAR_NAME ]; then wget $DOWNLOAD_PATH; fi
tar -xf $TAR_NAME
echo "unpacked to $UNTAR_DIR"
ABS_UNTAR_DIR=$(realpath $UNTAR_DIR)
echo "loading modules ..."
module purge
module load $(jq -r '.modules.compiler' <<< $CONFIG)
module load $(jq -r '.modules.mpi' <<< $CONFIG)
module load $(jq -r '.modules.other | @sh' <<< $CONFIG | tr -d "'")
module list

# now cd to $BUILD_DIR/build: note $BUILD_DIR must exist as it was where the .json file is
cd $BUILD_DIR
if [ ! -d "build" ]; then mkdir build; fi
cd build
CMAKE_OPTS=$(jq -r '.cmake | @sh' <<< $CONFIG | tr -d "'")
echo "running cmake ..."
cmake $ABS_UNTAR_DIR  $CMAKE_OPTS
echo "running make ..."
make
echo "running make check..."
make check
echo "running make install ..."
make install
