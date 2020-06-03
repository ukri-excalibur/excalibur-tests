Intel MPI Benchmarks:

https://software.intel.com/en-us/imb-user-guide

This runs PingPong (latency/bandwidth), Uniband and Biband (bandwidth) tests from the IMB-MPI1 suite.

# Installation

If using OpenHPC install a `perf-tools` package e.g.:

    sudo yum install ohpc-gnu8-perf-tools

This installs gnu8 and openmpi3 TODO: and mvapich2?.

If using Spack e.g.:

    spack install intel-mpi-benchmarks ^openmpi@4: fabrics=ucx schedulers=auto

Note openmpi v4 is required to integrate properly with Slurm via pmix. UCX is recommended to make selection of IB/RoCE considerably simpler.


# TODO
- add hpc-tests git describe to performance history
- add failures to performance history or current status
