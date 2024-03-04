# Usage

## Running benchmarks

Once you have set up Spack and ReFrame, you can execute a benchmark with

```sh
reframe -c benchmarks/apps/BENCH_NAME -r
```

where `benchmarks/apps/BENCH_NAME` is the directory where the benchmark is.  The command
above assumes you have the program `reframe` in your PATH.  If you have followed the instructions
to install using `pip` into the default directory, it should have been automatically added.
If it is not the case, call `reframe` with its relative or absolute path.

For example, to run the Sombrero benchmark in the `benchmarks/apps/sombrero` directory you can
use

```sh
reframe -c benchmarks/apps/sombrero -r
```

## Setting ReFrame command line options

ReFrame supports a variety of command-line options that can be useful, or sometimes necessary.

### System-specific options

While the aim is to automate as much system-specific configuration as possible, there are some options that have to be provided by the user, such as accounting details, and unfortunately the syntax can vary.
See [systems](../systems) for information about the use of this framework on specific systems.

### Performance report

You can use the `--performance-report` command-line option to ReFrame to get a nicely formatted performance report after the benchmark has completed.

### Selecting Spack build spec

For benchmarks that use the Spack build system, the tests define a default Spack specification
to be installed in the environment, but users can change it when invoking ReFrame on the
command line with the
[`-S`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-S) option to set
the `spack_spec` variable:

```sh
reframe -c benchmarks/apps/sombrero -r --performance-report -S spack_spec='sombrero@2021-08-16%intel'
```

### Selecting system and queue access options

The provided ReFrame configuration file contains the settings for multiple systems.  If you
use it, the automatic detection of the system may fail, as some systems may use clashing
hostnames.  To avoid this, you can use the flag [`--system
NAME:PARTITION`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-system)
to specify the system (and optionally the partition) to use.

Additionally, if submitting jobs to the compute nodes requires additional options, like for
example the resource group you belong to (for example `--account=...` for Slurm), you have
to pass the command line flag
[`--job-option=...`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-J)
to `reframe` (e.g., `--job-option='--account=...'`).

### Setting environment variables

All the built-in fields of ReFrame regression classes can be set on a per-job basis using the
`-S` command-line option. One useful such field is
[`env_vars`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.env_vars),
which controls the environment variables used in a job.
The syntax to set dictionary items, like for `env_vars`, is a comma-separated list of `key:value` pairs: `-S dict=key_1:value_1,key_2:value_2`.
For example

```sh
reframe -c benchmarks/apps/sombrero -r --performance-report -S env_vars=OMP_PLACES:threads
```

runs the `benchmarks/apps/sombrero` benchmark setting the environment variable `OMP_PLACES`
to `threads`.

## Usage on unsupported systems

The configuration provided in [`reframe_config.py`](./reframe_config.py) lets you run the
benchmarks on pre-configured HPC systems.  However you
can use this framework on any system by choosing the "default" system with `--system
default`, or by using your own ReFrame configuration.  You can use the "default" system to run
benchmarks in ReFrame without using a queue manager or an MPI launcher (e.g. on a personal workstation).

If you choose the "default" system and a benchmark using the Spack build system,
a new empty Spack environment will be automatically created in
`benchmarks/spack/default` when ReFrame is launched for the first time.
You should populate the environment with the packages already installed on your system
before running Spack to avoid excessively rebuilding system packages. See
[spack configuration](../contributing#spack-configuration) for instructions on how
to set up a Spack environment.
In particular, make sure that at least a compiler and an MPI library are added into the environment.
After the Spack environment is set up, tell ReFrame to use it by setting the environment
variable `EXCALIBUR_SPACK_ENV`, as described in [setup](../setup#spack).

## Selecting multiple benchmarks

ReFrame tests may contain tags that allow the user to select which tests to run. These can be leveraged to defined sets of benchmarks. To run all tests in a directory, pass the [`-R` flag](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-R) to ReFrame. Then filter down to a specific tag by passing the [`-t` flag](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-0).

For example, the [tag "example" is defined](https://github.com/ukri-excalibur/excalibur-tests/blob/1a7377e885977833c150569c32eb1db478f63087/benchmarks/examples/sombrero/sombrero.py#L113) in the sombrero example. To select the sombrero example out of all benchmarks, run

```bash
reframe -c benchmarks/ -R -r -t example
```

Tests can contain multiple tags. To create a custom set of benchmarks, add a new tag to the tests you want to include in the set.
