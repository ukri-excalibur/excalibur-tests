# Hemepure benchmark

HemeLB is a high performance lattice-Boltzmann solver optimized for simulating blood flow through sparse geometries, such as those found in the human vasculature. It is routinely deployed on powerful supercomputers, scaling to hundreds of thousands of cores even for complex geometries. HemeLB has traditionally been used to model cerebral blood flow and vascular remodelling in retinas, but is now being applied to simulating the fully coupled human arterial and venous trees.

HemePure is a optimized verion of HemeLB with improved memory, compilation and scaling

This directory includes a data directory, `input_data/pipe`, which can be used to benchmark both GPU and CPU machines. This data file was taken from https://github.com/UCL-CCS/HemePure/tree/master/cases/pipe.

The benchmarks are designed as strong scaling tests which run across multiple full nodes for a given system.

## Usage 

From the top-level directory of the repository, you can run the benchmarks with

```sh
reframe --system <your_system> -c benchmarks/apps/hemepure -r --performance-report
```

### Filtering the benchmarks

Note that, since we are running strong scaling tests over multiple nodes, the benchmarks may need to be filtered if usage rules restrict the size of jobs which can be run on any given system. To do this filtering, use the `-n` option like so

```sh
reframe --system <your_system> -c benchmarks/apps/hemepure -r --performance-report -n '.*num_nodes_param=<2|4|8|16>.*'
```

>NOTE: The GPU benchmarks are currently in complete and thus have been disabled
Again, depending on the system's rules/machine size, further filtering may be needed for GPU tests i.e.

```sh
reframe --system <your_system> -c benchmarks/apps/hemepure -r --performance-report -n '.*num_nodes_param=<2|4|8|16>.*num_gpus_per_node_param=<1|2|4>'
```

## Figure of Merit

The figure of merit captured by these benchmarks is the performance metric Runtime, measured in seconds. 

This output can be found in the stdout or `rfm_job.out` file within the output directory produced by Reframe. If the end of this file resembles what is shown below, the Rate `402.9466 s` would be captured.
```
[Rank 0000000, 4.024656e+02 s, 00000074207320 kB] :: time step 0050000 :: write_image_to_disk 1
[Rank 0000000, 4.024656e+02 s, 00000074221220 kB] :: time step 0050000 :: tau: 0.548000, max_relative_press_diff: 0.000, Ma: 0.006, max_vel_phys: 1.697326e-02
[Rank 0000000, 4.029466e+02 s, 00000074222464 kB] :: -------------------
[Rank 0000000, 4.029466e+02 s, 00000074224972 kB] :: SIMULATION FINISHED
```
