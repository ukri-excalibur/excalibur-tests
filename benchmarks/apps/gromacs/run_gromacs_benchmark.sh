#!/bin/bash -l

set -e

system=""
partition=""
build_system="spack"
compiler_path=""
gmx_dir="$PWD"
gpu_flavour="NONE"
simd_flavour="NONE"
excalibur_tests_dir="$HOME/excalibur-tests"
extra_flags=""

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
  echo "    -c <compiler_path>   The path to the compiler to use. Defaults to CC and CXX in env."
  echo "    -d <gmx_dir>         The path where GROMACS should be installed. Defaults to current"
  echo "                         working directory." 
  echo "    -g <gpu_flavour>     The flavour of GPU offloading to use, NONE, CUDA, OpenCL or SYCL."
  echo "                         Defaults to NONE (CPU)."
  echo "    -v <simd_flavour>    The flavour of SIMD to use. See gromacs documentation for options."
  echo "                         Defaults to NONE."
  echo "    -e <excalibur_dir>   The directory where the excalibur-tests dir is located. If not set,"
  echo "                         the default is $HOME/excalibur-tests."
  echo "    -f <extra_flags>     Extra flags to pass to the reframe command."
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
while getopts "hs:p:b:c:d:g:v:e:f:" opt
do
  case ${opt} in
    h  ) help;;
    s  ) system=$OPTARG;;
    p  ) partition=$OPTARG;;
    b  ) build_system=$OPTARG;;
    c  ) compiler_path=$OPTARG;;
    d  ) gmx_dir=$OPTARG;;
    g  ) gpu_flavour=$OPTARG;;
    v  ) simd_flavour=$OPTARG;;
    e  ) excalibur_tests_dir=$OPTARG;;
    f  ) extra_flags=$OPTARG;;
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
gromacs_config_dir="$excalibur_tests_dir/benchmarks/apps/gromacs/config"
if [ ! -d "$gromacs_config_dir" ]
then
    echo "Error: Could not find gromacs config in $excalibur_tests_dir. Searched $gromacs_config_dir."
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
      # Verify CC and CXX are set
      c_compiler="$CC"
      cxx_compiler="$CXX"
      if [ "$compiler_path" != "" ]; then
          export c_compiler="$compiler_path/bin/mpicc"
          export cxx_compiler="$compiler_path/bin/mpicxx"
      else 
        if [ "$CC" == "" ]; then
            echo "Env var CC is unset or set to the empty string"
            exit 1
        fi
        if [ -z "${CXX}" ]; then
            echo "Env var CXX is unset or set to the empty string"
            exit 1
        fi
      fi

      cd $gmx_dir
      if [ ! -d "gromacs-2024.4" ]; then
        echo "Extracting GROMACS src to $gmx_dir"
        curl -o "gromacs-2024.4.tar.gz" "https://ftp.gromacs.org/gromacs/gromacs-2024.4.tar.gz"
        tar xfz gromacs-2024.4.tar.gz
        rm gromacs-2024.4.tar.gz
      else
        echo "Found existing gromacs-2024.4 directory, $gmx_dir/gromacs-2024.4"
      fi
      
      cd gromacs-2024.4
      if [ -d "build" ]; then
        echo "Replacing existing build directory"
        rm -rf build
      fi
      echo "Changing into gromacs-2024.4/build"
      mkdir build
      cd build

      echo "Building GROMACS with cmake"
      cmake_command=$(cat <<-END 
				cmake .. \
				  -DCMAKE_C_COMPILER=$c_compiler \
				  -DCMAKE_CXX_COMPILER=$cxx_compiler \
				  -DGMX_MPI=on \
				  -DGMX_SIMD=$simd_flavour \
				  -DGMX_DOUBLE=on \
				  -DGMX_BUILD_OWN_FFTW=ON \
          -DGMX_FFT_LIBRARY=fftw3 \
				  $gpu_flags
			END
			)
      echo "$cmake_command"
      eval "$cmake_command"
      
      make_command="make -j"
      echo "$make_command"
      eval "$make_command"

      echo "Copying gmx_mpi_d executable into $gromacs_config_dir"
      cp "$gmx_dir/gromacs-2024.4/build/bin/gmx_mpi_d" "$gromacs_config_dir/gmx_mpi_d"
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

export_commands=$(cat <<-END 
export TMPDIR="${TMPDIR:-${XDG_RUNTIME_DIR:-/tmp}}";
export RFM_CONFIG_FILES="$excalibur_tests_dir/benchmarks/reframe_config.py";
export RFM_USE_LOGIN_SHELL="true";
END
)
echo "$export_commands"
eval "$export_commands"

# Activate excalibur env
if [ ! -d "$excalibur_tests_dir/.venv" ]
then
  echo "Error: no .venv found in $excalibur_tests_dir"
  exit 1
else
  activate_command="source "$excalibur_tests_dir/.venv/bin/activate""
  echo "$activate_command"
  eval "$activate_command"
fi

reframe_command="reframe --system $system_partition -c $excalibur_tests_dir/benchmarks/apps/gromacs/config -r $test_flags $extra_flags"
echo "$reframe_command"
eval "$reframe_command"
