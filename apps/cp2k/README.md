# CP2K benchmarks

[CP2K](https://www.cp2k.org/) is a quantum chemistry and solid state physics
software package.  This directory includes the `H2O-64` and `LiH_HFX` CP2K
benchmarks based on [ARCHER
2](https://github.com/hpc-uk/archer-benchmarks/tree/d6739bb77b798a0ef014c710e781d52fc7b206c5/apps/CP2K)
HPC benchmarks.

## Usage

From the top-level directory of the repository, you can run the benchmarks with

```sh
reframe -c apps/cp2k -r --performance-report
```

### Filtering the benchmarks

This will run both the `H2O-64` and `LiH_HFX` benchmarks.  You can run
individual benchmarks with the
[`--tag`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-0)
option:

* `h2o-64` to run the `H2O-64` benchmark,
* `lih-hfx` to run the `LiH_HFX` benchmark.

Examples:

```sh
reframe -c apps/cp2k -r --performance-report --tag h2o-64
reframe -c apps/cp2k -r --performance-report --tag lih-hfx
```

### Setting the number of threads and MPI processes

By default, these benchmarks will use

* [`num_cpus_per_task`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_cpus_per_task):
  2
* [`num_tasks`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_tasks):
  `current_partition.processor.num_cpus // min(1, current_partition.processor.num_cpus_per_core) // num_cpus_per_task`
* [`num_tasks_per_node`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_tasks_per_node): `num_tasks`

You can override the values of these variables from the command line with the
[`--setvar`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-S)
option, for example

```sh
reframe -c apps/cp2k -r --performance-report --setvar=num_cpus_per_task=4 --setvar=num_tasks=16
```

_**Note**_: you're responsible for overriding these variables in a consistent
way, so that, for example, `num_tasks_per_node` doesn't exceed the number of
total tasks runnable on each node.

## Figure of merit

The figure of merit captured by these benchmarks is the maximum total CP2K time.
For example, if the output of the program is

```
 -------------------------------------------------------------------------------
 -                                                                             -
 -                                T I M I N G                                  -
 -                                                                             -
 -------------------------------------------------------------------------------
 SUBROUTINE                       CALLS  ASD         SELF TIME        TOTAL TIME
                                MAXIMUM       AVERAGE  MAXIMUM  AVERAGE  MAXIMUM
 CP2K                                 1  1.0    0.178    0.295  200.814  200.816
 qs_energies                          1  2.0    0.000    0.000  200.091  200.093
 scf_env_do_scf                       1  3.0    0.000    0.000  198.017  198.018
 qs_ks_update_qs_env                  8  5.0    0.000    0.000  161.422  161.440
 rebuild_ks_matrix                    7  6.0    0.000    0.000  161.419  161.437
 qs_ks_build_kohn_sham_matrix         7  7.0    0.001    0.001  161.419  161.437
 hfx_ks_matrix                        7  8.0    0.000    0.000  154.464  154.495
```

the number `200.816` will be captured.
