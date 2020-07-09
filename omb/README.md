# OSU Micro-Benchmarks

http://mvapich.cse.ohio-state.edu/static/media/mvapich/README-OMB.txt

This runs various bandwidth and latency tests. See `reframe_omb.py` for full details.

# Installation - OpenHPC

Install a `perf-tools` package e.g.:

    sudo yum install ohpc-gnu8-perf-tools

This installs gnu8 and openmpi3 TODO: and mvapich2?.

# Installation - Spack

e.g.:

    spack install intel-mpi-benchmarks ^openmpi@4: fabrics=ucx schedulers=auto

See note in main README re. usage of spack with existing mpi library installations.
