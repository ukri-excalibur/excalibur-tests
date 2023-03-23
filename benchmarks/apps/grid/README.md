# GRID

ReFrame benchmarks for the [GRID](https://github.com/paboyle/Grid) code, a data
parallel C++ mathematical object library.

## Usage

From the top-level directory of the repository, you can run the benchmarks with

```sh
reframe -c benchmarks/apps/grid -r --performance-report
```

### Filtering the benchmarks

You can run individual benchmarks with the
[`--tag`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-0)
option.  At the moment we have the following tags:

* `ITT` to run the `Benchmark_ITT` application.

Examples:

```sh
reframe -c benchmarks/apps/grid -r --performance-report --tag ITT
```

### Options (memory, number of threads and MPI processes)

There are some options you can set to control the settings of the benchmark.
These are the currently available options, with their default values:

* `mpi`: `'1.1.1.1'`.  This is the string to pass to the benchmarking applications with the
  `--mpi` flag.  This will also automatically set the ReFrame variable
  [`num_tasks`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_tasks)
* [`num_cpus_per_task`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_cpus_per_task):
  `current_partition.processor.num_cpus // min(1, current_partition.processor.num_cpus_per_core)`
* [`num_tasks_per_node`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_tasks_per_node):
  `current_partition.processor.num_cpus // num_cpus_per_task`
* `shm`: `1024`.  This is the size of the shared memory used by the benchmark, in MiB, as an
  integer.

You can override the values of these variables from the command line with the
[`--setvar`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-S)
option, for example

```sh
reframe -c benchmarks/apps/grid -r --performance-report --setvar=mpi='2.2.1.1' --setvar=num_cpus_per_task=12
reframe -c benchmarks/apps/grid -r --performance-report --setvar=mpi='4.4.4.4' --setvar=shm=4096
```

_**Note**_: you're responsible for overriding these variables in a consistent
way, so that, for example, `num_tasks_per_node` doesn't exceed the number of
total tasks runnable on each node.

## Figure of merit

If the output of the program contains

```
Grid : Message : 380809 ms :  Comparison point  result: 143382.7 Mflop/s per node
```

the number `143382.7` will be captured as figure of merit.
