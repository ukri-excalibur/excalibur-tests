#!/bin/bash -l

# Setup
python3 -m venv demo-env
source ./demo-env/bin/activate
git clone git@github.com:ukri-excalibur/excalibur-tests.git
git clone -c feature.manyFiles=true git@github.com:spack/spack.git
source ./spack/share/spack/setup-env.sh
export RFM_CONFIG_FILES="$(pwd)/excalibur-tests/benchmarks/reframe_config.py"
export RFM_USE_LOGIN_SHELL="true"
python3 --version
pip --version
pip install --upgrade pip
pip install ./excalibur-tests

