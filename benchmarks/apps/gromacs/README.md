# GROMACS benchmark

[GROMACS]() is a free and open-source software suite for high-performance molecular dynamics and output analysis.
This directory includes a data file, `gromacs_1400k_atoms.tpr`, which can be used to benchmark both GPU and CPU machines. This data file was taken from https://www.hecbiosim.ac.uk/access-hpc/benchmarks.

The benchmarks are designed as strong scaling tests which run across multiple full nodes for a given system.

## Usage 

Without filtering, all benchmarks (CPU and GPU) will be run. This is unlikely to be what we want. Therefore, from the top-level directory of the repository, you can run the benchmarks using tags to filter for CPU benchmarks.

```sh
reframe --system <your_system> -c benchmarks/apps/gromacs -r --tag cpu --performance-report
```

Or GPU benchmarks.

```sh
reframe --system <your_system> -c benchmarks/apps/gromacs -r --tag gpu --performance-report
```

### Filtering the benchmarks

Note that, since we are running strong scaling tests over multiple nodes, the benchmarks may need to be further filtered if usage rules restrict the size of jobs which can be run on any given system. To do this filtering, use the `-n` option like so

```sh
reframe --system <your_system> -c benchmarks/apps/gromacs -r --tag cpu --performance-report -n '.*num_nodes_param=<2|4|8|16>.*'
```

Again, depending on the system's rules/machine size, additional filtering may be needed for GPU tests i.e.

```sh
reframe --system <your_system> -c benchmarks/apps/gromacs -r --tag gpu --performance-report -n '.*num_nodes_param=<2|4|8|16>.*num_gpus_per_node_param=<1|2|4>'
```

## Figure of Merit

The figure of merit captured by these benchmarks is the performance metric Rate, measured in ns/day. Here, ns/day refers to the number of nanoseconds of simulation that you can do in a day of computation.

This output can be found in the `md.log` file within the output directory produced by Reframe. If the end of this file resembles was as below, the Rate `4.892` would be captured.
```
               Core t (s)   Wall t (s)        (%)
       Time:    28258.913      353.239     7999.9
                 (ns/day)    (hour/ns)
Performance:        4.892        4.906
Finished mdrun on rank 0 Tue Apr  1 13:43:36 2025
```
