# ExCALIBUR tests

Performance benchmarks and regression tests for the ExCALIBUR project.

These benchmarks are based on a similar project by
[StackHPC](https://github.com/stackhpc/hpc-tests).

_**Note**: at the moment the ExCALIBUR benchmarks are a work-in-progress._

## Installation

It is recommended to install the **excalibur-tests** package with `pip` by

```sh
pip install .
```

On most systems, it is recommended to install the package in a virtual environment.
For example, using the python3 [built-in virtual environment tool `venv`](https://docs.python.org/3/library/venv.html),
create an environment called `my_environment` with

```sh
python3 -m venv ./my_environment
```

and activate it with

```sh
source ./my_environment/bin/activate
```

For [development](https://setuptools.pypa.io/en/latest/userguide/development_mode.html),
pass the `-e/--editable` flag to `pip` to link the installed package to the files in the local
directory, instead of copying, to be able to make changes to the installed package.

## Requirements

The pip install will install a compatible version of **ReFrame** from
[PyPi](https://pypi.org/project/ReFrame-HPC/). However, you will have to
manually provide an installation of **Spack**.

### Spack

_**Note**: we require Spack 0.18.  In some HPC facilities there may be already a
central Spack installation available.  In principle you should be able to use a
system installation of Spack (you only need to have `spack` in the `PATH`), but
you need to make sure the version is recent enough to install the required
packages and understand the provided environments.  Instructions below show you
how to install Spack locally._

[Spack](https://spack.io/) is a package manager specifically designed for HPC
facilities.  Follow the [official
instructions](https://spack.readthedocs.io/en/latest/getting_started.html) to
install the latest version of Spack.

In order to use Spack in ReFrame, the framework we use to run the benchmarks
(see below), the directory where the `spack` program is installed needs to be in
the `PATH` environment variable.  This can be achieved for instance by running
the commands to get shell support described in Spack documentation, which you
can also add to your shell init script to do it automatically in every session.
For example, if you use a shell of the family bash/zsh/sh you can add to your
init script:

```sh
export SPACK_ROOT="/path/to/spack"
if [ -f "${SPACK_ROOT}/share/spack/setup-env.sh" ]; then
    source "${SPACK_ROOT}/share/spack/setup-env.sh"
fi
```

replacing `/path/to/spack` with the actual path to your Spack installation.

ReFrame requires a [Spack
Environment](https://spack.readthedocs.io/en/latest/environments.html).  We
provide Spack environments for some of the systems that are part of the
ExCALIBUR and DiRac projects.  If you want to use a different Spack environment,
set the environment variable `EXCALIBUR_SPACK_ENV` to the path of the directory
where the environment is.  If this is not set, ReFrame will try to use the
environment for the current system, if known, otherwise it will automatically
create a very basic environment.

### ReFrame

[ReFrame](https://reframe-hpc.readthedocs.io/en/stable/) is a high-level
framework for writing regression tests for HPC systems.  For our tests we
require ReFrame 3 version 3.11.0, or later. We are currently not compatible
with ReFrame 4.

If you need to manually install ReFrame, follow the [official
instructions](https://reframe-hpc.readthedocs.io/en/stable/started.html) to
install this package.  Note that ReFrame requires Python 3.6: in your HPC system
you may need to load a specific module to have this version of Python available.

We provide a ReFrame configuration file with the settings of some systems that
are part of the ExCALIBUR project.  You can point ReFrame to this file by
setting the
[`RFM_CONFIG_FILE`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#envvar-RFM_CONFIG_FILE)
environment variable:

```sh
export RFM_CONFIG_FILE="${PWD}/reframe_config.py"
```

If you want to use a different ReFrame configuration file, for example because
you use a different system, you can set this environment variable to the path of
that file.

**Note**: in order to use the Spack build system in ReFrame, the `spack`
executable must be in the `PATH`, also on the computing nodes of a cluster, if
you want to run your benchmarks on them.  Note that by default ReFrame uses

```sh
!#/bin/bash
```

as [shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)), which would not load
the user's init script.  If you have added Spack to your `PATH` within your init
script, you may want to set the
[`RFM_USE_LOGIN_SHELL`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#envvar-RFM_USE_LOGIN_SHELL)
environment variable in order to make ReFrame use

```sh
!#/bin/bash -l
```

as shebang line, instead.

## Usage

Once you have set up Spack and ReFrame, you can execute a benchmark with

```sh
reframe -c apps/BENCH_NAME -r --performance-report
```

where `apps/BENCH_NAME` is the directory where the benchmark is.  The command
above supposes you have the program `reframe` in your PATH, if it is not the
case you can also call `reframe` with its relative or absolute path.  For
example, to run the Sombrero benchmark in the `apps/sombrero` directory you can
use

```sh
reframe -c apps/sombrero -r --performance-report
```

For benchmark using the Spack build system, the tests define a default Spack specification
to be installed in the environment, but users can change it when invoking ReFrame on the
command line with the
[`-S`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-S) option to set
the `spack_spec` variable:

```
reframe -c apps/sombrero -r --performance-report -S spack_spec='sombrero@2021-08-16%intel'
```

Note that the `-S` option can be used to set from the command line on a per-job
basis the built-in fields of ReFrame regressions classes, e.g.
[`variables`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.variables),
which controls the environment variables used in a job.  For example

```
reframe -c apps/sombrero -r --performance-report -S variables=OMP_PLACES:threads
```

runs the `apps/sombrero` benchmark setting the environment variable `OMP_PLACES`
to `threads`.

### Selecting system and queue access options

The provided ReFrame configuration file contains the settings for multiple systems.  If you
use it, the automatic detection of the system may fail, as some systems may use clashing
hostnames.  You can always use the flag [`--system
NAME:PARTITION`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-system)
to specify the system (and optionally the partition) to use.

Additionally, if submitting jobs to the compute nodes requires additional options, like for
example the resource group you belong to (for example `--account=...` for Slurm), you have
to pass the command line flag
[`--job-option=...`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-J)
to `reframe` (e.g., `--job-option='--account=...'`).

### Unsupported systems

The configuration provided in [`reframe_config.py`](./reframe_config.py) lets you run the
benchmarks on systems for which the configuration has been already contributed.  However you
can still use this framework on any system by choosing the "generic" system with `--system
generic`, or using your own ReFrame configuration.  Note, however, that if you use the
"generic" system, ReFrame will not know anything about the queue manager of your system, if
any, or the MPI launcher.  For the benchmarks using the Spack build system, if you choose
the "generic" system, a new empty Spack environment will be automatically created in
`spack-environments/generic`.  In any case, you can always make the benchmarks use a
different Spack environment by setting the environment variable `EXCALIBUR_SPACK_ENV`
described above.

## Contributing new systems or benchmarks

Feel free to add new benchmark apps or support new systems that are part of the
ExCALIBUR benchmarking collaboration.  Read
[`CONTRIBUTING.md`](./CONTRIBUTING.md) for more details.
