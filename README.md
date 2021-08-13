# ExCALIBUR tests

Performance benchmarks and regression tests for the ExCALIBUR project.

These benchmarks are based on a similar project by
[StackHPC](https://github.com/stackhpc/hpc-tests).

_**Note**: at the moment the ExCALIBUR benchmarks are a work-in-progress._

## Requirements

### Spack

_**Note**: in some HPC facilities there may be already a central Spack
installation available.  In principle you should be able to use that one (you
only need to set the `SPACK_ROOT` environment variable), but you may need an
up-to-date version of Spack in order to install some packages.  Instructions
below show you how to install Spack locally._

[Spack](https://spack.io/) is a package manager specifically designed for HPC
facilities.  Follow the [official
instructions](https://spack.readthedocs.io/en/latest/getting_started.html) to
install the latest version of Spack.  Remember to run the commands to get shell
support, or add them to your shell init script to do it automatically.  For
example, if you use a shell of the family bash/zsh/sh you can add to your init
script:

```sh
export SPACK_ROOT="/path/to/spack"
if [ -f "${SPACK_ROOT}/share/spack/setup-env.sh" ]; then
    source "${SPACK_ROOT}/share/spack/setup-env.sh"
fi
```

replacing `/path/to/spack` with the actual path to Spack.

ReFrame, the framework we use to run the benchmarks (see below) requires a
[Spack Environment](https://spack.readthedocs.io/en/latest/environments.html).
We provide Spack environments for some of the systems that are part of the
ExCALIBUR project.  If you want to use a different Spack environment, set the
environment variable `EXCALIBUR_SPACK_ENV` to the path of the directory where
the environment is.  If this is not set, ReFrame will try to use the environment
for the current system, if known, otherwise it will automatically create a very
basic environment.

### ReFrame

[ReFrame](https://reframe-hpc.readthedocs.io/en/stable/) is a high-level
framework for writing regression tests for HPC systems.  For our tests we
require ReFrame 3.7.3.  Follow the [official
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

## Usage

TODO: expand

```sh
/path/to/reframe/bin/reframe -c apps/hpgmg -r --performance-report
/path/to/reframe/bin/reframe -c apps/sombrero -r --performance-report
```

The provided ReFrame configuration file contains the settings for multiple
systems.  If you use it, the automatic detection of the system may fail, as some
systems may use clashing hostnames.  You can always use the flag [`--system
NAME:PARTITION`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-system)
to specify the system (and optionally the partition) to use.
