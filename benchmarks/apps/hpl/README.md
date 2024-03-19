# High Performance Linpack

Run Intel optimised HPL tests on one and all nodes.

## Requirements

### Intel HPL

This uses the pre-built binaries supplied with [Intel's MKL package](https://www.intel.com/content/www/us/en/docs/onemkl/developer-guide-windows/2024-0/overview-intel-distribution-for-linpack-benchmark.html).
***Note***: Intel MPI is also required.

By default the `intel-mkl` and `intel-mpi` Spack recipes will be used.
If these packages are already available on the system you are using and the Spack environment knows about them, the system packages will be automatically used, otherwise Spack will download and install them for you.

If you want to use the oneAPI distribution of MKL and MPI, pass `--setvar spack_spec="intel-oneapi-mkl ^intel-oneapi-mpi"` as additional argument to the ReFrame invocation (see below).
As usual, if these packages are available in the system and the Spack environment knows about them, those packages will be used.

### `HPL.dat` configuration files

Appropriate `HPL.dat` configuration files must be generated and placed in `<repo_root>/benchmarks/apps/hpl/<sysname>/<number of tasks>`, if not already available.
ReFrame will copy these files into the staging directories before running a test, so changes made to these files will persist and apply to the next run.

Hints:

- Generally, set PxQ to equal number of nodes, with P equal or smaller than Q (as using 1x MPI rank per node)
- Select problem size *N* to use e.g. 80% of total memory
- Check [Intel documentation](https://www.intel.com/content/www/us/en/docs/onemkl/developer-guide-linux/2024-0/configuring-parameters.html) to select appropriate block size *NB*
- When running, check on a single node that `pstree` and `top` appear as expected.

***Note***: not all systems have appropriate input data, or not for the number of tasks you want to run, so you may have to create the `HPL.DAT` file yourself.

If you want to use an `HPL.dat` file in a different directory, you can pass `--setvar config_dir=<DIRECTORY>` as additional argument to the ReFrame invocation (see below), where `<DIRECTORY>` is the absolute path of the directory where `HPL.dat` is.

## Running tests

Run using e.g.:

```
reframe -c benchmarks/apps/hpl --run --performance-report
```

You can set the number of nodes and tasks per node to use by setting the following variables:

* [`num_tasks_per_node`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_tasks_per_node) (default = 1)
* [`num_tasks`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_tasks) (default = 1)

For example

```
reframe -c benchmarks/apps/hpl --run --performance-report --setvar num_tasks=4 # 4 MPI ranks
reframe -c benchmarks/apps/hpl --run --performance-report --setvar num_tasks=8 --setvar num_tasks_per_node=2 # 8 MPI ranks, 2 for each node (for a total of 4 nodes)
```

## Outputs

The ReFrame performance variable is:

- `Gflops`: The performance.
