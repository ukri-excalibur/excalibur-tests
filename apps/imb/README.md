# Intel MPI Benchmarks

https://software.intel.com/en-us/imb-user-guide

This runs the following MPI1 tests:
- PingPong (latency/bandwidth) on 2x nodes using 1x process per node
- Uniband and Biband (bandwidth) 2x nodes using a range of processes per node from 1 up to as many as there are physical cores.

# Installation - OpenHPC

Install a `perf-tools` package e.g.:

    sudo yum install ohpc-gnu8-perf-tools

This installs gnu8, openmpi3 and mvapich2.

# Installation - Spack

e.g.:

    spack install intel-mpi-benchmarks ^/<mpi_library_hash>

See note in main README re. usage of spack with existing mpi library installations.

# Configurating ReFrame

See main README.

# Running

Run all tests e.g.:
        
    cd hpc-tests
    conda activate hpc-tests
    reframe/bin/reframe -C reframe_config.py -c apps/imb/ --run --performance-report

The following tags are defined:
    - Test name, one of "pingpong", "biband", "uniband".
    - For uniband and biiband tests only: "procs_per_node=N" where N is 2, 4, ..., etc.
