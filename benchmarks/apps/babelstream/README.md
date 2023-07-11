# BabelStream benchmarks

[BabelStream](https://github.com/UoB-HPC/BabelStream) 

Measure memory transfer rates to/from global device memory on GPUs. This benchmark is similar in spirit, and based on, the STREAM benchmark [1] for CPUs.
Unlike other GPU memory bandwidth benchmarks this does not include the PCIe transfer time.
There are multiple implementations of this benchmark in a variety of programming models.
This code was previously called GPU-STREAM.

## Usage

From the top-level directory of the repository, you can run the benchmarks with

```sh
reframe -c benchmarks/apps/babelstream -r  --tag <TAG> --system=<ENV:PARTITION> -Sbuild_locally=false -Sspack_spec='babelstream +tag <extra flags>'
```

### Filtering the benchmarks
The Spack directives for the babelstream could be found [here](https://github.com/spack/spack/tree/develop/var/spack/repos/builtin/packages/babelstream)
You can run individual benchmarks with the [`--tag`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-0) option:

* `omp`to run the `OpenMP` benchmark.
* `ocl` to run the `OpenCL` benchmark.
* `std` to run the `STD` benchmark.
* `std20`to run the `STD20` benchmark.
* `hip` to run the `HIP` benchmark.
* `cuda`to run the `CUDA` benchmark.
* `kokkos` to run the `Kokkos` benchmark.
* `sycl` to run the `SYCL` benchmark.
* `sycl2020` to run the `SYCL2020` benchmark.
* `acc` to run the `ACC` benchmark.
* `raja` to run the `RAJA` benchmark.
* `tbb` to run the `TBB` benchmark.
* `thrust` to run the `THRUST` benchmark,


Examples:

```sh
reframe -c benchmarks/apps/babelstream -r --tag omp --system=isambard-macs:volta -S build_locally=false -S spack_spec='babelstream%gcc@9.2.0 +omp cuda_arch=70'
reframe -c benchmarks/apps/babelstream -r --tag tbb --system=isambard-macs:cascadelake -S build_locally=false -S spack_spec='babelstream@develop +tbb'
reframe -c benchmarks/apps/babelstream -r --tag cuda --system=isambard-macs:volta -S build_locally=false -S spack_spec='babelstream@develop%gcc@9.2.0 +cuda cuda_arch=70'
```

### Setting the number of threads and MPI processes

By default, these benchmarks will use


* [`num_gpus_per_node`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_gpus_per_node: This value is by default 1 for the benchmarks requiring GPU. (e.g. CUDA,HIP) 

You can override the value of this variable from the command line with the
[`--setvar`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-S)
option, for example

```sh
reframe -c benchmarks/apps/babelstream -r --tag cuda --system=isambard-macs:volta -S build_locally=false -S spack_spec='babelstream@develop%gcc@9.2.0 +cuda cuda_arch=70' --setvar=num_gpus_per_node=2
```

_**Note**_: you're responsible for overriding this variable in a consistent
way, so that, for example, `num_gpus_per_node` doesn't exceed the number of
total GPUs runnable on each node.

## Figure of merit

The figure of merit captured by these benchmarks is the bandwidth.
For example, if the output of the program is

```
BabelStream
Version: 4.0
Implementation: OpenMP
Running kernels 100 times
Precision: double
Array size: 268.4 MB (=0.3 GB)
Total size: 805.3 MB (=0.8 GB)
Function    MBytes/sec  Min (sec)   Max         Average     
Copy        91018.241   0.00590     0.01087     0.00721     
Mul         80014.622   0.00671     0.01173     0.00837     
Add         92644.967   0.00869     0.01636     0.01121     
Triad       93484.396   0.00861     0.01416     0.01142     
Dot         114688.364  0.00468     0.01382     0.00707
```

the output numbers 

```
Copy : 91018.241
Mul : 80014.622
Add : 92644.967 
Triad : 93484.396
Dot : 114688.364
```

 will be captured.
