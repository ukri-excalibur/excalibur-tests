#!/bin/bash -l

set -e

# Store starting directory
initial_working_dir="$PWD"

system=""
partition=""
module_list=""
build_system="spack"
c_compiler=""
cxx_compiler=""
gmx_dir="$PWD"
gpu_flavour="NONE"
simd_flavour="NONE"
excalibur_tests_dir="$HOME/excalibur-tests"
reframe_flags=""

help() {
  echo "Usage: $0 -s <system> [-p <partition>] [-b <build_system>] [-c <c_compiler>] [-x <cxx_compiler>] [-d <gmx_dir>] [-g <gpu_flavour>] [-v <simd_flavour>] [-e <excalibur_tests_dir>] [-f <reframe_flags>]"
  echo ""
  echo "Flags:"
  echo "    -s|--system <system>                The name of the system to set for reframe."
  echo "    -m|--module-list <module_list>      A comma seperated list of modules to load before running the benchmark."
  echo ""
  echo "  Optional:"
  echo "    -p|--partition <partition>          The name of the system partition to set for reframe. If not set, just"
  echo "                                        the system name will be used."
  echo "    -b|--build-type <build_type>        The type of build desired, spack, cmake or run_only. Defaults to spack."
  echo "                                        Note: for the cmake build, the C and C++ compilers are extracted from"
  echo "                                        the environment variables CC and CXX."
  echo "    -c|--c-compiler <compiler_path>     The path to the c compiler to use. Defaults to CC in env."
  echo "    -x|--cxx-compiler <compiler_path>   The path to the c++ compiler to use. Defaults to CXX in env."
  echo "    -d|--gmx-dir <gmx_dir>              The path where GROMACS should be installed. Defaults to current"
  echo "                                        working directory." 
  echo "    -g|--gpu-flavour <gpu_flavour>      The flavour of GPU offloading to use, NONE, CUDA, OpenCL or SYCL."
  echo "                                        Defaults to NONE (CPU)."
  echo "    -v|--simd-flavour <simd_flavour>    The flavour of SIMD to use. See gromacs documentation for options."
  echo "                                        Defaults to NONE."
  echo "    -e|--excalibur-dir <excalibur_dir>  The directory where the excalibur-tests dir is located. If not set,"
  echo "                                        the default is $HOME/excalibur-tests."
  echo "    -f|--reframe-flags <reframe_flags>  Extra flags to pass to the reframe command."
  echo "    -h                                  Display this help message."
  exit 0
}

expect_option() {
  if [ "$2" == "" ]
  then
      echo "Invalid option: $1 requires an argument" >&2
      help
  fi
}

# check for no input arguments and show help
if [ $# -eq 0 ];
then
    help
    exit 0
fi

# parse input arguments
while [ $# -gt 0 ]
do
  case $1 in
    -h | --help                ) help;;
    -s | --system              ) expect_option "$1" "$2"; system=$2; shift 2;;
    -p | --partition           ) expect_option "$1" "$2"; partition=$2; shift 2;;
    -m | --module-list         ) expect_option "$1" "$2"; module_list=${2//,/ }; shift 2;;
    -b | --build-system        ) expect_option "$1" "$2"; build_system=$2; shift 2;;
    -c | --c-compiler          ) expect_option "$1" "$2"; c_compiler=$2; shift 2;;
    -x | --cxx-compiler        ) expect_option "$1" "$2"; cxx_compiler=$2; shift 2;;
    -d | --gmx-dir             ) expect_option "$1" "$2"; gmx_dir=$2; shift 2;;
    -g | --gpu-flavour         ) expect_option "$1" "$2"; gpu_flavour=$2; shift 2;;
    -v | --simd-flavour        ) expect_option "$1" "$2"; simd_flavour=$2; shift 2;;
    -e | --excalibur-tests-dir ) expect_option "$1" "$2"; excalibur_tests_dir=$2; shift 2;;
    -f | --reframe-flags       ) expect_option "$1" "$2"; reframe_flags=$2; shift 2;;
    *                          ) echo "Invalid option: $1" >&2; help;;
  esac
done

# Verify required inputs
if [ "$system" == "" ]
then
    echo "Error: System must be set"
    help
fi
gromacs_config_dir="$excalibur_tests_dir/benchmarks/apps/gromacs/config"
if [ ! -d "$gromacs_config_dir" ]
then
    echo "Error: Could not find gromacs config in $excalibur_tests_dir. Searched $gromacs_config_dir."
    exit 1
fi
if [ "$module_list" == "" ]
then
    if [ $system != "local" ]
    then
        echo "Error: module list must be set"
        help
    fi
    echo "Running local build, no modules required"
else
    echo "Unloading all modules"
    module purge
    echo "Loading user provided modules: $module_list"
    module load $module_list
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
      # Verify compilers are set
      if [ "$c_compiler" == "" ]; then
          if [ $CC == "" ]
          then
            echo "Unable to determine c compiler"
            exit 1
          else
            c_compiler="$CC"
          fi
      fi

      if [ "$cxx_compiler" == "" ]; then
          if [ $CXX == "" ]
          then
            echo "Unable to determine c++ compiler"
            exit 1
          else
            cxx_compiler="$CXX"
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
      cmake_command="cmake .."
      cmake_command="$cmake_command -DCMAKE_C_COMPILER=$c_compiler"
      cmake_command="$cmake_command -DCMAKE_CXX_COMPILER=$cxx_compiler"
      cmake_command="$cmake_command -DGMX_MPI=on"
      cmake_command="$cmake_command -DGMX_SIMD=$simd_flavour"
      cmake_command="$cmake_command -DGMX_DOUBLE=on"
      cmake_command="$cmake_command -DGMX_BUILD_OWN_FFTW=ON"
      cmake_command="$cmake_command -DGMX_FFT_LIBRARY=fftw3"
      cmake_command="$cmake_command $gpu_flags"
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

# Ensure we run reframe command from the initial working directory
cd "$initial_working_dir"

reframe_command="reframe --system $system_partition -c $excalibur_tests_dir/benchmarks/apps/gromacs/config -r $test_flags $reframe_flags"
echo "$reframe_command"
eval "$reframe_command"
