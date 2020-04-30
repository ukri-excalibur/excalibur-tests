#!/usr/bin/bash
#set -x #echo on
set -e # die on error
# NB: DCMAKE_INSTALL_PREFIX is a bit confusing as it is relative to build.json, NOT the cwd

CONFIG=$(<$1)
GROMACS_VER=$(jq -r '.version' <<< $CONFIG)
TAR_NAME="gromacs-${GROMACS_VER}.tar.gz"
UNTAR_DIR="gromacs-${GROMACS_VER}" # assumption about tar structure!
DOWNLOAD_PATH="http://ftp.gromacs.org/pub/gromacs/${TAR_NAME}"
CONF_DIR="$(dirname $1)"
BUILD_DIR="${CONF_DIR}/build/"
INSTALL_PREFIX=$(jq -r '.cmake."-DCMAKE_INSTALL_PREFIX"' <<< $CONFIG)
INSTALL_DIR=$(realpath $CONF_DIR/$INSTALL_PREFIX)
echo "Will build v$GROMACS_VER in $BUILD_DIR & install to $INSTALL_DIR"

# start in the pwd, i.e. hpc-tests/gromacs:
echo "downloading and unpacking ..."
if [ ! -f $TAR_NAME ]; then wget $DOWNLOAD_PATH; fi
#tar -xf $TAR_NAME
echo "unpacked to $UNTAR_DIR"
ABS_UNTAR_DIR=$(realpath $UNTAR_DIR)
echo "loading modules ..."
module purge
module load $(jq -r '.modules.compiler' <<< $CONFIG)
module load $(jq -r '.modules.mpi' <<< $CONFIG)
module load $(jq -r '.modules.other | @sh' <<< $CONFIG | tr -d "'")
module list

# now cd to $BUILD_DIR (is relative to the config file)
mkdir -p $BUILD_DIR
cd $BUILD_DIR
CMAKE_OPTS=$(jq -r '.cmake | [to_entries[] | "\(.key)=\(.value)"] | join(" ")' <<< $CONFIG | tr -d "'") # turns the dict into a single line "k1=v1 k2=v2 ..."
echo "running cmake ..."
cmake $ABS_UNTAR_DIR  $CMAKE_OPTS
echo "running make ..."
make
echo "running make check..."
#make check
echo "running make install ..."
make install
