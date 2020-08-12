# Gromacs

Performance tests of the Gromacs molecular dynamics code http://www.gromacs.org/ using benchmarks from HECBioSim: http://www.hecbiosim.ac.uk/benchmarks:
    - 61K atom system - 1WDN Glutamine-Binding Protein
    - 1.4M atom system - A Pair of hEGFR Dimers of 1IVO and 1NQL
    - 3M atom system - A Pair of hEGFR tetramers of 1IVO and 1NQL

Note Gromacs 2016 is required due to the benchmark file used.

Each benchmark is run on a range of number of nodes, from 1 up to all available. Each run uses as many processes per node as there are physical cores.

The following performance variables are captured:
- 'ns_per_day': Nano-seconds of simulation completed per day
- 'hour_per_ns': Hours required per nano-second of simulation
- 'core_t' (s): Gromacs-reported CPU time (sum for all processes)
- 'wall_t' (s): Gromacs-reported wall-clock time
- 'runtime_real' (s): Wallclock time reported by `time` for entire MPI program start to finish (i.e. may include additional setup/teardown time not captured in 'wall_t').


# Installation - OpenHPC

NB: The Gromacs docs recommend using `fftw`. While this is available as the OpenHPC package `fftw-gnu8-openmpi3-ohpc` the Gromacs docs recommend letting Gromacs install its own.

This assumes e.g.:
 - cmake
 - gnu8-compilers-ohpc
 - openmpi3-gnu8-ohpc


```
wget http://ftp.gromacs.org/pub/gromacs/gromacs-2016.4.tar.gz
tar -xf gromacs-2016.4.tar.gz
cd gromacs-2016.4
mkdir build_mpi
cd build_mpi
module load gnu8 openmpi3
cmake ../ -DGMX_MPI=ON -DGMX_OPENMP=ON -DGMX_GPU=OFF -DGMX_X11=OFF -DGMX_DOUBLE=OFF -DGMX_BUILD_OWN_FFTW=ON -DREGRESSIONTEST_DOWNLOAD=ON -DCMAKE_INSTALL_PREFIX=<wherever>
make
make check
make install # to DCMAKE_INSTALL_PREFIX above
```

# Installation - Spack

e.g.:

    spack install gromacs@2016.4 ^openmpi@4: fabrics=ucx schedulers=auto

Default variants should be appropriate.

See note in main README re. mpi libraries.

# Usage

Run using e.g.:
        
    cd hpc-tests
    conda activate hpc-tests
    reframe/bin/reframe -C reframe_config.py -c apps/gromacs/ --run --performance-report
    
Or for example, to run only the 61k atom case for 1 node only a single partition:
    
    reframe/bin/reframe -C reframe_config.py -c apps/gromacs/ --run --performance-report --system alaska:ib-openmpi4-ucx -n 'Gromacs_61k_1$'
