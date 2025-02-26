#!/bin/bash -l

system=""
partition=""
test_name=""
excalibur_tests_dir="$HOME/excalibur-tests"

help() {
  echo "Usage:"
  echo "    -h              Display this help message."
  echo "    -s <system>     The name of the system to set for reframe."
  echo "    -p <partition>  Optional: The name of the system partition to set for reframe."
  echo "                              If not set, just the system name will be used."
  echo "    -t <test_name>  Optional: The name of a single test to run."
  echo "    -e <dir>        Optional: The directory where excalibur-tests is located."
  echo "                              If not set, the default is $HOME/excalibur-tests."
  exit 0
}

# check for no input arguments and show help
if [ $# -eq 0 ];
then
    help
    exit 0
fi

# parse input arguments
while getopts "hs:p:t:e:" opt
do
  case ${opt} in
    h  ) help;;
    s  ) system=$OPTARG;;
    p  ) partition=$OPTARG;;
    t  ) test_name=$OPTARG;;
    e  ) excalibur_tests_dir=$OPTARG;;
    \? ) echo "Invalid option: $OPTARG" >&2; exit 1;;
  esac
done
shift $((OPTIND -1))

if [ "$system" == "" ]
then
    echo "System must be set"
    exit 1
fi

system_partition="$system"
if [ "$partition" != "" ]
then
    system_partition="$system:$partition"
fi

test_flags=""
if [ "$test_name" != "" ]
then
    test_flags="-n $test_name"
fi

export TMPDIR="${TMPDIR:-${XDG_RUNTIME_DIR:-/tmp}}"
export RFM_CONFIG_FILES="$excalibur_tests_dir/benchmarks/reframe_config.py"
export RFM_USE_LOGIN_SHELL="true"

# Activate excalibur env
source "$excalibur_tests_dir/.venv/bin/activate"

reframe --system "$system_partition" -c "$excalibur_tests_dir/benchmarks/apps/gromacs" -r "$test_flags"