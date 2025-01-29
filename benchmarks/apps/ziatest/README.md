# Ziatest

ReFrame benchmarks for [Ziatest](https://gitlab.com/NERSC/N10-benchmarks/ziatest), which is intended to provide a realistic assessment of both launch and wireup requirements of MPI applications.

## Usage

From the top-level directory of the repository, you can run the benchmarks with

```sh
reframe -c benchmarks/apps/ziatest -r --performance-report
```

### Options (memory, number of threads and MPI processes)

There are some options you can set to control the settings of the benchmark.
These are the currently available options, with their default values:

* [`num_tasks`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_tasks): 1
* [`num_tasks_per_node`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_tasks_per_node): 1.

You can override the values of these variables from the command line with the [`--setvar`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-S) option, for example

```sh
reframe -c benchmarks/apps/ziatest -r --performance-report --setvar=num_tasks=16
reframe -c benchmarks/apps/ziatest -r --performance-report --setvar=num_tasks=256 --setvar=num_tasks_per_node=16
```

## Figure of merit

If the output of the program contains a line like

```
Time test was completed in   0:01 min:sec
```

or

```
Time test was completed in   233.70 millisecs
```

the time will be captured as figure of merit and always reported in seconds.
