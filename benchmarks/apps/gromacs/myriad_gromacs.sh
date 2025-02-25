#!/bin/bash -l

export TMPDIR="${TMPDIR:-${XDG_RUNTIME_DIR:-/tmp}}"
export RFM_CONFIG_FILES="$HOME/excalibur-tests/benchmarks/reframe_config.py"
export RFM_USE_LOGIN_SHELL="true"

# Activate excalibur env
source $HOME/excalibur-tests/.venv/bin/activate

reframe --system myriad:cpu -c "$HOME/excalibur-tests/benchmarks/apps/gromacs" -r -n ThreadAndRankVariationTest