# Installation

## Excalibur-tests

### Requirements

**Python version 3.7** or later is required. 

### Virtual environments

On most systems, it is recommended to install 
the package in a virtual environment. For example, using the python3 
[built-in virtual environment tool `venv`](https://docs.python.org/3/library/venv.html),
create an environment called `my_environment` with

```sh
python3 -m venv ./my_environment
```

and activate it with

```sh
source ./my_environment/bin/activate
```

### Installation

First, clone the git repository

```sh
git clone https://github.com/ukri-excalibur/excalibur-tests.git
```

Install the **excalibur-tests** package and the necessary dependencies with `pip` by

```sh
pip install -e ./excalibur-tests
```

### Notes

The `-e/--editable` flag is recommended for two reasons.

- Spack installs packages in a `opt` directory under the spack environment. With `-e` the spack
environment remains in your local directory and `pip` creates symlinks to it. Without `-e` spack
will install packages inside your python environment.
- For [development](https://setuptools.pypa.io/en/latest/userguide/development_mode.html),
the `-e` flag to `pip` links the installed package to the files in the local
directory, instead of copying, to allow making changes to the installed package.

Note that to use `-e` with a project configured with a `pyproject.toml` you need `pip` version 22 or later.

## Spack

The `pip install` command will install a compatible version of **ReFrame** from
[PyPi](https://pypi.org/project/ReFrame-HPC/). However, you will have to
manually provide an installation of **Spack**.

[Spack](https://spack.io/) is a package manager specifically designed for HPC
facilities. In some HPC facilities there may be already a central Spack installation available.
However, the version installed is most likely too old to support all the features
used by this package. Therefore we recommend you install the latest version locally,
following the instructions below.

Follow the [official instructions](https://spack.readthedocs.io/en/latest/getting_started.html)
to install the latest version of Spack (summarised here for convenience, but not guaranteed to be
up-to-date):

### Installation

Git clone the spack repository
```sh
git clone -c feature.manyFiles=true https://github.com/spack/spack.git
```
Run spack setup script 
```sh
source ./spack/share/spack/setup-env.sh
```
Check spack is in `$PATH`, for example 
```sh
spack --version
```

### Notes

_**Note**: if you have already installed spack locally and you want to upgrade to
a newer version, you might first have to clear the cache to avoid conflicts:
`spack clean -m`_

