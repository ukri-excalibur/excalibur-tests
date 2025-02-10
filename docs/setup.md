# Configuration

## Pre-configured systems

A number of UK-based HPC systems that are part of the DiRAC and ExCALIBUR programs 
have been pre-configured. See [systems](systems.md), or [https://github.com/ukri-excalibur/excalibur-tests/tree/main/benchmarks/spack/](https://github.com/ukri-excalibur/excalibur-tests/tree/main/benchmarks/spack) for a list. 
On these systems the ReFrame configuration and Spack environment are included in the 
`excalibur-tests` repository and all you need to do is point the framework to them.

### ReFrame

You can point ReFrame to the provided config file by setting the
[`RFM_CONFIG_FILES`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#envvar-RFM_CONFIG_FILES)
environment variable:

```sh
export RFM_CONFIG_FILES="<path-to-excalibur-tests>/benchmarks/reframe_config.py"
```

If you want to use a different ReFrame configuration file, for example because
you use a different system, you can set this environment variable to the path of
that file.

**Note**: in order to use the Spack build system in ReFrame, the `spack`
executable must be in the `PATH` also on the compute nodes of a cluster, if
you want to run your benchmarks on them. This is taken care of by adding it
to your init file (see spack section below).

However, you will also need to set the
[`RFM_USE_LOGIN_SHELL`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#envvar-RFM_USE_LOGIN_SHELL)
environment variable 
```sh
export RFM_USE_LOGIN_SHELL="true"
``` 
in order to make ReFrame use `!#/bin/bash -l` as 
[shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)) line, which would load
the user's init script.

### Spack

In order to use Spack in ReFrame, 
the directory where the `spack` program is installed needs to be in
the `PATH` environment variable. This is taken care of by the `setup-env.sh`
script run in [install](install.md#installation_2). To have spack available in every session,
you can have your shell init script (e.g. `.bashrc`)
re-run it automatically, by adding the following lines to it:
```sh
export SPACK_ROOT="/path/to/spack"
if [ -f "${SPACK_ROOT}/share/spack/setup-env.sh" ]; then
    source "${SPACK_ROOT}/share/spack/setup-env.sh"
fi
```
replacing `/path/to/spack` with the actual path to your Spack installation.

## New systems

We need the [ReFrame](https://reframe-hpc.readthedocs.io/en/stable/)
configuration and a Spack environment for a new system.

### ReFrame

Add a new system to the ReFrame configuration in
`benchmarks/reframe_config.py`.  Read [ReFrame documentation about
configuration](https://reframe-hpc.readthedocs.io/en/stable/configure.html) for
more details, or see the examples of the existing systems.  

**Note**: you likely do
not need to customise the programming environment in ReFrame, as we will use
Spack as build system, which will deal with that.

If available, the command `lscpu`, run on a compute node, is typically useful to
get information about the CPUs, to be used in the `processor` item of the system
configuration.  The numbers you need to watch out for are:

* "CPU(s)", (`num_cpus` in ReFrame configuration),
* "Thread(s) per core", (`num_cpus_per_core`),
* "Socket(s)", (`num_sockets`),
* "Core(s) per socket", (`num_cpus_per_socket`).

### Spack

When using Spack as build system, ReFrame needs a [Spack
environment](https://spack.readthedocs.io/en/latest/environments.html) to run
its tests. The Spack environment is separate and independent of the python
virtual environment. Follow these steps to create a Spack environment for a new system:

#### Create the environment
```sh
spack env create --without-view -d /path/to/environment
```
Remember to
[disable views](https://spack.readthedocs.io/en/latest/environments.html#filesystem-views)
with `--without-view` to avoid conflicts when installing incompatible packages
in the same environment

#### Activate the environment
```sh
spack env activate -d /path/to/environment
```

#### Set [`install_tree`](https://spack.readthedocs.io/en/latest/config_yaml.html#install-tree)
```sh
spack config add 'config:install_tree:root:$env/opt/spack'
```

#### Add compilers

Make sure the compilers you want to add are in the `PATH` (e.g., load the
relevant modules), then add them to the Spack environment with:
```sh
spack compiler find
```

#### Add external packages

Add other packages (e.g., MPI): make sure the package you want to add are
"visible" (e.g., load the relevant modules) and add them to the environment
with
```sh
spack external find PACKAGE-NAME ...
```
where `PACKAGE-NAME ...` are the names of the corresponding Spack packages

#### Set `EXCALIBUR_SPACK_ENV` variable

To use the new Spack environment in ReFrame,
set the environment variable `EXCALIBUR_SPACK_ENV` to the path of the directory
where the environment is, i.e.
```sh
export EXCALIBUR_SPACK_ENV=/path/to/environment
```
If this is not set, ReFrame will try to use the
environment for the current system if known, otherwise it will automatically
create a very basic environment (see [Usage on unsupported systems](use.md#usage-on-unsupported-systems).

#### (optional) Make manual tweaks

If necessary, manually tweak the environment. For example, if there is already
a global Spack available in the system, you can [include its configuration
files](https://spack.readthedocs.io/en/latest/environments.html#included-configurations),
or [add its install trees as
upstreams](https://spack.readthedocs.io/en/latest/chain.html).
 

#### (optional) Add spack repositories

If you are using a custom repo for spack package recipes (see *Spack package* below), add
it to the spack environment with
```sh
spack -e /path/to/environment repo add /path/to/repo
```

#### (optional) Override default spack cache path

Spack also, by default, keeps various caches and user data in `~/.spack`, but users may want to override these locations. Spack provides environment variables that allow you to override or opt out of configuration locations:

`SPACK_USER_CONFIG_PATH`: Override the path to use for the user scope (`~/.spack` by default).

`SPACK_SYSTEM_CONFIG_PATH`: Override the path to use for the system scope (`/etc/spack` by default).

`SPACK_USER_CACHE_PATH`: Override the default path to use for user data (misc_cache, tests, reports, etc.)

For more details, see [spack docs](https://spack.readthedocs.io/en/latest/configuration.html#overriding-local-configuration).
