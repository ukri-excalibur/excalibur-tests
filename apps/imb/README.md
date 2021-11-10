# Intel MPI Benchmarks

https://software.intel.com/en-us/imb-user-guide

Builds automatically using spack.

Runs the following MPI1 tests using Intel MPI and OpenMPI:
- PingPong (latency/bandwidth) on 2 nodes using 1 process per node
- Uniband and Biband (bandwidth) using a range of processes from 2 up to 256 using default task pinning (Fill up nodes one by one)

The following tags are defined:
    - Test mode, one of "pingpong", "biband", "uniband".
    - MPI implementation, one of "openmpi", "intel-mpi"
