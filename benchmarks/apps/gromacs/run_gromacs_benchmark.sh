#!/bin/bash -l

system=""
partition=""
build_system="spack"
gmx_dir="$PWD"
gpu_flavour="NONE"
simd_flavour="NONE"
excalibur_tests_dir="$HOME/excalibur-tests"

help() {
  echo "Usage: $0 -s <system> [-p <partition>] [-b <build_type>] [-r] [-p <gmx_dir>] [-g] [-e <excalibur_dir>]"
  echo ""
  echo "Flags:"
  echo "    -s <system>          The name of the system to set for reframe."
  echo ""
  echo "  Optional:"
  echo "    -p <partition>       The name of the system partition to set for reframe. If not set, just"
  echo "                         the system name will be used."
  echo "    -b <build_type>      The type of build desired, spack, cmake or run_only. Defaults to spack."
  echo "                         Note: for the cmake build, the C and C++ compilers are extracted from"
  echo "                         the environment variables CC and CXX."
  echo "    -p <gmx_dir>         The path where GROMACS should be installed. Defaults to current"
  echo "                         working directory." 
  echo "    -g <gpu_flavour>     The flavour of GPU offloading to use, NONE, CUDA, OpenCL or SYCL."
  echo "                         Defaults to NONE (CPU)."
  echo "    -v <simd_flavour>    The flavour of SIMD to use. See gromacs documentation for options."
  echo "                         Defaults to NONE."
  echo "    -e <excalibur_dir>   The directory where the excalibur-tests dir is located. If not set,"
  echo "                         the default is $HOME/excalibur-tests."
  echo "    -h                   Display this help message."
  exit 0
}

# check for no input arguments and show help
if [ $# -eq 0 ];
then
    help
    exit 0
fi

# parse input arguments
while getopts "hs:p:b:p:g:v:e:" opt
do
  case ${opt} in
    h  ) help;;
    s  ) system=$OPTARG;;
    p  ) partition=$OPTARG;;
    b  ) build_system=$OPTARG;;
    p  ) gmx_dir=$OPTARG;;
    g  ) gpu_flavour=$OPTARG;;
    v  ) simd_flavour=$OPTARG;;
    e  ) excalibur_tests_dir=$OPTARG;;
    \? ) echo "Invalid option: $OPTARG" >&2; exit 1;;
  esac
done
shift $((OPTIND -1))

# Verify required inputs
if [ "$system" == "" ]
then
    echo "System must be set"
    exit 1
fi

# Set the system we are running on
system_partition="$system"
if [ "$partition" != "" ]
then
    system_partition="$system:$partition"
fi

# Build GROMACS if build type is cmake
if [ "$build_system" == "cmake" ]
then
    # Build GPU flags
    gpu_flags=""
    if [ "$gpu_flavour" != "NONE" ]
    then
      gpu_flags="-DGMX_GPU=$gpu_flavour"
    fi

    # Check if build dir exists
    if [ ! -d "$gmx_dir" ]; then
      echo "Error: $gmx_dir does not exist"
      exit 1
    else
      # Build GROMACS
      cd $gmx_dir
      curl -o "gromacs-2024.4.tar.gz" "https://ftp.gromacs.org/gromacs/gromacs-2024.4.tar.gz"
      tar xfz gromacs-2024.4.tar.gz
      rm gromacs-2024.4.tar.gz
      cd gromacs-2024.4
      mkdir build
      cd build
      cmake .. \
        -DCMAKE_C_COMPILER=$CC \
        -DCMAKE_CXX_COMPILER=$CXX \
        -DGMX_MPI=on \
        -DGMX_SIMD=$simd_flavour \
        -DGMX_DOUBLE=on \
        -DGMX_FFT_LIBRARY=fftw3 \
        $gpu_flags
      make
    fi
fi

# Determine the reframe test we wish to run
test_flags="-n StrongScaling"
if [ "$build_system" == "run_only" ] || [ "$build_system" == "cmake" ]
then
    test_flags="${test_flags}RunOnly"
elif [ "$build_system" == "spack" ]
then
    test_flags="${test_flags}Spack"
else
    echo "Invalid build system: $build_system"
    exit 1
fi

if [ "$gpu_flavour" != "NONE" ]
then
    test_flags="${test_flags}GPU"
else
    test_flags="${test_flags}CPU"
fi

test_flags="${test_flags}Benchmark"

export TMPDIR="${TMPDIR:-${XDG_RUNTIME_DIR:-/tmp}}"
export RFM_CONFIG_FILES="$excalibur_tests_dir/benchmarks/reframe_config.py"
export RFM_USE_LOGIN_SHELL="true"

# Activate excalibur env
if [ ! -d "$excalibur_tests_dir/.venv" ]
then
  echo "Error: no .venv found in $excalibur_tests_dir"
  exit 1
else
  source "$excalibur_tests_dir/.venv/bin/activate"
fi

reframe --system $system_partition -c $excalibur_tests_dir/benchmarks/apps/gromacs/config -r $test_flags
