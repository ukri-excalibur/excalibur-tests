# SOMBERO

[SOMBRERO](https://github.com/sa2c/sombrero) is a benchmarking utility 
for high performance computing based on lattice field theory applications.

SOMBRERO is composed of 6 similar benchmarks 
that are based on different lattice field theories, 
each one with a different arithmetic intensity 
and a different compute/communication balance.
Each benchmark consists of a fixed number (50)
of iterations of the Conjugate Gradient algorithm,
using the underlying Lattice Dirac operator 
built in the relative theory.

See the [documentation](https://github.com/sa2c/sombrero) 
for more information.

SOMBRERO uses a pure-mpi parallelisation. 

Each of these benchmarks is launched 
on a range of number of processes
(depending on the setup of the machine)
and 4 different lattice sizes.

The following performance variables are captured:
- 'flops' : the computing performance (Gflop/second)
- 'time' : time spent in the CG algorithm (seconds)
- 'communicated': number of bytes communicated via MPI (bytes)
- 'avg_arithmetic_intensity': average arithmetic intensity (from DRAM or L3) (Flops/byte)
- 'computation/communication': the ratio of floating point operations 
                               over the bytes communicated.

