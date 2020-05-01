#!/usr/bin/bash
# Usage:
#  build.sh path/to/build.json
#

#set -x #echo on
set -e # die on error

CONFIG=$(realpath $1) # makes it cd-proof
GROMACS_VER=$(jq -r '.version' $CONFIG)
TAR_NAME="gromacs-${GROMACS_VER}.tar.gz"
UNTAR_DIR="gromacs-${GROMACS_VER}" # assumption about tar structure!
DOWNLOAD_PATH="http://ftp.gromacs.org/pub/gromacs/${TAR_NAME}"
CONF_DIR="$(dirname $1)"
BUILD_DIR="$(realpath ${CONF_DIR}/build/)"
INSTALL_DIR=$(realpath ${CONF_DIR}/install/)
echo "Will build v$GROMACS_VER in $BUILD_DIR & install to $INSTALL_DIR"

# start in the pwd, i.e. hpc-tests/gromacs:
echo "downloading and unpacking ..."
if [ ! -f $TAR_NAME ]; then wget $DOWNLOAD_PATH; fi
tar -xf $TAR_NAME
echo "unpacked to $UNTAR_DIR"
ABS_UNTAR_DIR=$(realpath $UNTAR_DIR)
echo "loading modules ..."
module purge
module load $(jq -r '.modules.compiler' $CONFIG)
module load $(jq -r '.modules.mpi' $CONFIG)
module load $(jq -r '.modules.other | @sh' $CONFIG | tr -d "'")
module list

# now cd to $BUILD_DIR
mkdir -p $BUILD_DIR
cd $BUILD_DIR
CMAKE_OPTS="$(jq -r '.cmake | join(" ")' $CONFIG | tr -d "'") -DCMAKE_INSTALL_PREFIX=$INSTALL_DIR"
echo "running cmake ..."
cmake $ABS_UNTAR_DIR $CMAKE_OPTS 
echo "running make ..."
make
echo "running make check..."
make check
echo "running make install ..."
make install
