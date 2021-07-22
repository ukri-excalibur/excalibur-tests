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

### ReFrame

[ReFrame](https://reframe-hpc.readthedocs.io/en/stable/) is a high-level
framework for writing regression tests for HPC systems.  For our tests we
require ReFrame 3.6.2.  Follow the [official
instructions](https://reframe-hpc.readthedocs.io/en/stable/started.html) to
install this package.  Note that ReFrame requires Python 3.6: in your HPC system
you may need to load a specific module to have this version of Python available.

TODO: provide ReFrame configuration files, and explain how to use them:

```sh
export RFM_CONFIG_FILE="/path/to/reframe-settings.py"
```

## Usage

TODO: expand

```sh
/path/to/reframe/bin/reframe -c apps/hpgmg/reframe_hpgmg.py -r --performance-report
/path/to/reframe/bin/reframe -c apps/sombrero/reframe_sombrero.py -r --performance-report
```
