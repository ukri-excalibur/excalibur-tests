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

There are four benchmark cases that can be chosen 
using the `--tag=<TAG>` command line option of `reframe`:
- `mini`: A debug run, on a very small lattice, on 2 processes.
- `ITT-sn`: A run on a single node, using all the cores in each node 
   (as described [here](https://github.com/sa2c/sombrero/wiki/Dirac-ITT-2020-Benchmarks)).
- `ITT-64n`: A run on 64 nodes, using all the cores in each node
   (as described [here](https://github.com/sa2c/sombrero/wiki/Dirac-ITT-2020-Benchmarks)).
   The number of nodes used can be changed by setting the variable `num_nodes`,
   for example `reframe ... -S num_nodes=48`.
- `scaling`: A large benchmarking campaign, where of the benchmarks is launched 
             on a range of number of processes
             (depending on the setup of the machine)
             and 4 different lattice sizes 
             (details depend on how the cases are filtered).
In all these cases, the benchmark for each theory is launched.

The following performance variables are captured:
- 'flops' : the computing performance (Gflop/second)
- 'time' : time spent in the CG algorithm (seconds)
- 'communicated': number of bytes communicated via MPI (bytes)
- 'avg_arithmetic_intensity': average arithmetic intensity (from DRAM or L3) (Flops/byte)
- 'computation/communication': the ratio of floating point operations 
                               over the bytes communicated.

