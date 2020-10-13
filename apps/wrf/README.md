# Weather Research and Forecasting (WRF) Model

Results from WRF, the [Weather Research & Forecasting Model](https://www.mmm.ucar.edu/weather-research-and-forecasting-model) using the [WRFV3 benchmarks](https://www2.mmm.ucar.edu/wrf/WG2/benchv3/):
- 12km CONUS (medium-size case):
    > 48-hour, 12km resolution case over the Continental U.S. (CONUS) domain October 24, 2001 with a time step of 72 seconds. The benchmark period is hours 25-27 (3 hours), starting from a restart file from the end of hour 24.
- 2.5km CONUS (large case):
    > Latter 3 hours of a 9-hour, 2.5km resolution case covering the Continental U.S. (CONUS) domain June 4, 2005 with a 15 second time step.  The benchmark period is hours 6-9 (3 hours), starting from a restart file from the end of the initial 6 hour period
Descriptions from the above benchmark page.

Each benchmark is run on a range of number of nodes, from 1 up to all available. Each run uses as many mpi tasks (processes) per node as there are physical cores.

The following performance variables are captured:
- 'gflops': Gigaflops per second, calculated as described in the [benchmark page](https://www2.mmm.ucar.edu/wrf/WG2/benchv3/), using the average time required per model timestep and the number of floating point operations required
  for the benchmark. The time required for each model timestep is reported by WRF itself.
- 'runtime_real' (s): Wallclock time reported by `time` for entire MPI program start to finish (i.e. including setup/teardown time).


# Installation

Installation of WRF and its dependencies can be difficult. Note that:
- The CONUS benchmarks require WRF v3.
- At least some versions of WRF v3 are [known](https://akirakyle.com/WRF_benchmarks/results.html#observations) not to compile with GNU compilers > 6.3.0.
- The CONUS benchmarks apparently do not benefit from using Parallel NetCDF.

An example install on the cascade-lake-based `csd-cclake` system using a system-installed Intel toolchain was as follows:

```shell
#!/bin/bash

export WRF_BUILD_DIR=~/wrf-build-icc19-impi19-hsw
module purge
module load rhel7/default-ccl # loads Intel compilers 19.1.2.254 and Intel MPI 2019 Update 8
export CC=icc
export CXX=icc
export FC=ifort
export F77=ifort
export DM_FC=mpiifort

# prep for build:
mkdir -p $WRF_BUILD_DIR/LIBRARIES
DIR=$WRF_BUILD_DIR/LIBRARIES

# build netcdf
cd $DIR
[ ! -f netcdf-4.1.3.tar.gz ] && wget http://www2.mmm.ucar.edu/wrf/OnLineTutorial/compile_tutorial/tar_files/netcdf-4.1.3.tar.gz
[ ! -d netcdf-4.1.3 ] && tar -xzf netcdf-4.1.3.tar.gz
cd netcdf-4.1.3
./configure --prefix=$DIR/netcdf --disable-dap --disable-netcdf-4 --disable-shared
make clean
make
make install
make check
export PATH=$DIR/netcdf/bin:$PATH
export NETCDF=$DIR/netcdf

# build WRF
cd $WRF_BUILD_DIR
[ ! -f WRFV3.8.1.TAR.gz ] && wget http://www2.mmm.ucar.edu/wrf/src/WRFV3.8.1.TAR.gz
if [ ! -d WRFV3.8.1 ]; then
    tar -xzf WRFV3.8.1.TAR.gz
    mv WRFV3 WRFV3.8.1
fi
cd WRFV3.8.1
./clean
export WRFIO_NCD_LARGE_FILE_SUPPORT=1
./configure <<< 67 # (dm+sm)   INTEL (ifort/icc): HSW/BDW
sed -i 's/DM_CC           =       mpicc/DM_CC           =       mpicc -DMPI2_SUPPORT/' configure.wrf
# Remove '-xHost':
sed 's/-xHost //' -i configure.wrf
# Change architecture flag:
sed "s/-xCORE-AVX2/-march=core-avx2/" -i configure.wrf
# Fix -openmp:
sed 's/-openmp /-qopenmp -qoverride-limits /' -i configure.wrf
./compile em_real >& log.compile
```
# Usage

Run using e.g.:
        
    cd hpc-tests
    conda activate hpc-tests
    reframe/bin/reframe -C reframe_config.py -c apps/wrf/ --run --performance-report
    
A precursor test automatically downloads the required benchmark files. This may take some time due to the files size. Because of this test, running only a single case requires a command like:
    
    reframe/bin/reframe -C reframe_config.py -c apps/wrf/ --run --performance-report --name WRF_2_5km_run_csd3_cclake_ib_icc19_impi19_ucx_3136_56 --name WRF_2_5km_download
    