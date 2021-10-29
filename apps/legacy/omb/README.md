# OSU Micro-Benchmarks

http://mvapich.cse.ohio-state.edu/static/media/mvapich/README-OMB.txt

The following tests are run (extracted performance variables described in brackets):

On 2x nodes using 1x process per node:
- osu_bw - bandwidth (max value over all message sizes)
- osu_latency - latency (min value over all message sizes)
- osu_bibw - bi-directional bandwidth (max value over all message sizes)

On 2x nodes using as many processes per node as there are physical cores:
- osu_allgather - latency (mean value calculated at each message size over pairs, then min taken over all message sizes)
- osu_allreduce - as above
- osu_alltoall - as above

On 2x nodes using a range of processes per node from 1 up to as many as there are physical cores:
- osu_mbw_mr - bandwidth and message rate (max value over all pairs and message sizes)

The following tags are defined:
    - Test name, as given above without the leading "osu_"
    - "procs_per_node=N" where N is as described above for the relevant test

# Installation - OpenHPC

Install a `perf-tools` package e.g.:

    sudo yum install ohpc-gnu8-perf-tools

This installs gnu8, openmpi3 (and mvapich2) as well as OMB.

# Installation - Spack

Install package `osu-micro-benchmarks` with default variants.

See note in main README re. usage of spack with existing mpi library installations.

# Configurating ReFrame

See main README.

# Running
Run all tests using e.g.:
        
    cd hpc-tests
    conda activate hpc-tests
    reframe/bin/reframe -C reframe_config.py -c apps/omb/ --run --performance-report
