# ExCALIBUR tests

Performance benchmarks and regression tests for the ExCALIBUR project.

These benchmarks are based on a similar project by
[StackHPC](https://github.com/stackhpc/hpc-tests).

_**Note**: at the moment the ExCALIBUR benchmarks are a work-in-progress._

## Installation

We require Python version 3.7 or later. Install the **excalibur-tests** package with `pip` by

```sh
pip install -e .
```

The `-e/--editable` flag is recommended for two reasons. 
- Spack installs packages in a `opt` directory under the spack environment. With `-e` the spack
environment remains in your local directory and `pip` creates symlinks to it. Without `-e` spack 
will install packages inside your python environment.
- For [development](https://setuptools.pypa.io/en/latest/userguide/development_mode.html),
the `-e` flag to `pip` links the installed package to the files in the local
directory, instead of copying, to allow making changes to the installed package.

Note that to use `-e` with a project configured with a `pyproject.toml` you need `pip` version 22 or later.

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

### Spack

The `pip install` command will install a compatible version of **ReFrame** from
[PyPi](https://pypi.org/project/ReFrame-HPC/). However, you will have to
manually provide an installation of **Spack**.

[Spack](https://spack.io/) is a package manager specifically designed for HPC
facilities. In some HPC facilities there may be already a central Spack installation available.
However, the version installed is most likely too old to support all the features
used by this package. Therefore we recommend you install the latest version locally, 
following the instructions below.

_**Note**: if you have already installed spack locally and you want to upgrade to 
a newer version, you might first have to clear the cache to avoid conflicts: 
`spack clean -m`_

Follow the [official instructions](https://spack.readthedocs.io/en/latest/getting_started.html) 
to install the latest version of Spack (summarised here for convenience, but not guaranteed to be 
up-to-date):
- git clone spack:
`git clone -c feature.manyFiles=true https://github.com/spack/spack.git`
- run spack setup script: `source ./spack/share/spack/setup-env.sh`
- check spack is in `$PATH`, for example `spack --version`

In order to use Spack in ReFrame, the framework we use to run the benchmarks
(see below), the directory where the `spack` program is installed needs to be in
the `PATH` environment variable. This is taken care of by the `setup-env.sh` 
script as above, and you can have your shell init script (e.g. `.bashrc`)
do that automatically in every session, by adding the following lines to it:
```sh
export SPACK_ROOT="/path/to/spack"
if [ -f "${SPACK_ROOT}/share/spack/setup-env.sh" ]; then
    source "${SPACK_ROOT}/share/spack/setup-env.sh"
fi
```
replacing `/path/to/spack` with the actual path to your Spack installation.

ReFrame also requires a [Spack
Environment](https://spack.readthedocs.io/en/latest/environments.html).  We
provide Spack environments for some of the systems that are part of the
ExCALIBUR and DiRAC projects in
[https://github.com/ukri-excalibur/excalibur-tests/tree/main/benchmarks/spack/](https://github.com/ukri-excalibur/excalibur-tests/tree/main/benchmarks/spack).
If you want to use a different Spack environment,
set the environment variable `EXCALIBUR_SPACK_ENV` to the path of the directory
where the environment is.  If this is not set, ReFrame will try to use the
environment for the current system if known, otherwise it will automatically
create a very basic environment (see "Usage on unsupported systems" section below).

## Configuration

### ReFrame

[ReFrame](https://reframe-hpc.readthedocs.io/en/stable/) is a high-level
framework for writing regression tests for HPC systems.  For our tests we
require ReFrame v4.1.3.

We provide a ReFrame configuration file with the settings of some systems that
are part of the ExCALIBUR or DiRAC projects.  You can point ReFrame to this file by
setting the
[`RFM_CONFIG_FILES`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#envvar-RFM_CONFIG_FILES)
environment variable:

```sh
export RFM_CONFIG_FILES="${PWD}/benchmarks/reframe_config.py"
```

If you want to use a different ReFrame configuration file, for example because
you use a different system, you can set this environment variable to the path of
that file.

**Note**: in order to use the Spack build system in ReFrame, the `spack`
executable must be in the `PATH` also on the compute nodes of a cluster, if
you want to run your benchmarks on them. This is taken care of by adding it 
to your init file (see spack section above).

However, you will also need to set the
[`RFM_USE_LOGIN_SHELL`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#envvar-RFM_USE_LOGIN_SHELL)
environment variable (`export RFM_USE_LOGIN_SHELL="true"`) in order to make ReFrame use

```sh
!#/bin/bash -l
```

as [shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)) line, which would load
the user's init script.

## Usage

Once you have set up Spack and ReFrame, you can execute a benchmark with

```sh
reframe -c benchmarks/apps/BENCH_NAME -r --performance-report
```

where `benchmarks/apps/BENCH_NAME` is the directory where the benchmark is.  The command
above assumes you have the program `reframe` in your PATH.  If you have followed the instructions
to install using `pip` into the default directory, it should have been automatically added.
If it is not the case, call `reframe` with its relative or absolute path.

For example, to run the Sombrero benchmark in the `benchmarks/apps/sombrero` directory you can
use

```sh
reframe -c benchmarks/apps/sombrero -r --performance-report
```

For benchmarks that use the Spack build system, the tests define a default Spack specification
to be installed in the environment, but users can change it when invoking ReFrame on the
command line with the
[`-S`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-S) option to set
the `spack_spec` variable:

```
reframe -c benchmarks/apps/sombrero -r --performance-report -S spack_spec='sombrero@2021-08-16%intel'
```

### Setting environment variables

All the built-in fields of ReFrame regression classes can be set on a per-job basis using the 
`-S` command-line option. One useful such field is 
[`env_vars`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.env_vars),
which controls the environment variables used in a job.
The syntax to set dictionary items, like for `env_vars`, is a comma-separated list of `key:value` pairs: `-S dict=key_1:value_1,key_2:value_2`.
For example

```
reframe -c benchmarks/apps/sombrero -r --performance-report -S env_vars=OMP_PLACES:threads
```

runs the `benchmarks/apps/sombrero` benchmark setting the environment variable `OMP_PLACES`
to `threads`.

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

### Usage on unsupported systems

The configuration provided in [`reframe_config.py`](./reframe_config.py) lets you run the
benchmarks on pre-configured HPC systems.  However you
can use this framework on any system by choosing the "default" system with `--system
default`, or by using your own ReFrame configuration.  You can use the "default" system to run 
benchmarks in ReFrame without using a queue manager or an MPI launcher (e.g. on a personal workstation).

If you choose the "default" system and a benchmark using the Spack build system,
a new empty Spack environment will be automatically created in
`benchmarks/spack/default` when ReFrame is launched for the first time. 
You should populate the environment with the packages already installed on your system
before running Spack to avoid excessively rebuilding system packages. See the 
*Spack configuration* section of [`CONTRIBUTING.md`](./CONTRIBUTING.md) for instructions on how 
to set up a Spack environment.
In particular, make sure that at least a compiler and an MPI library are added into the environment. 
After the Spack environment is set up, tell ReFrame to use it by setting the environment 
variable `EXCALIBUR_SPACK_ENV`, as described above.


### System-specific flags

While the aim is to automate as much system-specific configuration as possible, there are some options that have to be provided by the user, such as accounting details, and unfortunately the syntax can vary.
The file [`SYSTEMS.md`](./SYSTEMS.md) contains information about the use of this framework on specific systems.

## Contributing new systems or benchmarks

Feel free to add new benchmark apps or support new systems that are part of the
ExCALIBUR benchmarking collaboration.  Read [`CONTRIBUTING.md`](./CONTRIBUTING.md) for more details.
