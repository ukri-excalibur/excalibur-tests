# How to contribute to ExCALIBUR tests

You are welcome to contribute new application benchmarks and new systems part of
the ExCALIBUR benchmarking effort.

## New systems

We need the [ReFrame](https://reframe-hpc.readthedocs.io/en/stable/)
configuration and a Spack environment for the system.

### ReFrame configuration

Add a new system to the ReFrame configuration in
[`reframe_config.py`](./reframe_config.py).  Read [ReFrame documentation about
configuration](https://reframe-hpc.readthedocs.io/en/stable/configure.html) for
more details, or see the examples of the existing systems.  Note: you likely do
not need to customise the programming environment in ReFrame, as we will use
Spack as build system, which will deal with that.

### Spack configuration

When using Spack as build system, ReFrame needs a [Spack
environment](https://spack.readthedocs.io/en/latest/environments.html) to run
its tests.  We provide already configured Spack environments in the
[`spack-environments`](./spack-environments) directory, for each system in the
ReFrame configuration.

Here are the steps to create a Spack environment for a new system:

* create the environment:
  ```
  spack env create -d spack-environments/SYSTEM-NAME
  ```
  where `SYSTEM-NAME` is the same name as the ReFrame system name
* activate it:
  ```
  spack env activate -d spack-environments/SYSTEM-NAME
  ```
* set the
  [`install_tree`](https://spack.readthedocs.io/en/latest/config_yaml.html#install-tree):
  ```
  spack config add 'config:install_tree:root:opt/spack'
  ```
* make sure the compilers you want to add are in the `PATH` (e.g., load the
  relevant modules), then add them to the Spack environment with:
  ```
  spack compilers find
  ```
* add other packages (e.g., MPI): make sure the package you want to add are
  "visible" (e.g., load the relevant modules) and add them to the environment
  with
  ```
  spack external find --not-buildable PACKAGE-NAME ...
  ```
  where `PACKAGE-NAME ...` are the names of the corresponding Spack packages
* manually tweak the environment as necessary.  For example, if there is already
  a global Spack available in the system, you can [include its configuration
  files](https://spack.readthedocs.io/en/latest/environments.html#included-configurations),
  or [add its install trees as
  upstreams](https://spack.readthedocs.io/en/latest/chain.html).

## New tests

TODO
