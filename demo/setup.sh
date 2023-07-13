#!/bin/bash -l

system=$1

# System specific part of setup. Mostly load the correct python module
if [ $system == archer2 ]
then
    module load cray-python
    cd /work/d193/d193/tk-d193
elif [ $system == csd3 ]
then
    module load python/3.8
elif [ $system == cosma ]
then
    module swap python/3.10.7
elif [ $system == isambard ]
then
    module load python37
    export PATH=/home/ri-tkoskela/.local/bin:$PATH
fi

# Setup
mkdir demo
cd demo
python3 --version
python3 -m venv demo-env
source ./demo-env/bin/activate
git clone git@github.com:ukri-excalibur/excalibur-tests.git
git clone -c feature.manyFiles=true git@github.com:spack/spack.git
source ./spack/share/spack/setup-env.sh
export RFM_CONFIG_FILES="$(pwd)/excalibur-tests/benchmarks/reframe_config.py"
export RFM_USE_LOGIN_SHELL="true"
pip install --upgrade pip
pip install -e ./excalibur-tests

