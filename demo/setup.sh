#!/bin/bash

# Setup
mkdir benchmark-portability-demo
cd benchmark-portability-demo
python3 -m venv demo-env
source ./demo-env/bin/
git clone git@github.com:ukri-excalibur/excalibur-tests.git
git clone -c feature.manyFiles=true https://github.com/spack/spack.
source ./spack/share/spack/setup-env.sh
export RFM_CONFIG_FILES="$(PWD)/excalibur-tests/benchmarks/reframe_config.py"
export RFM_USE_LOGIN_SHELL="true"
pip install ./excalibur-tests

