# How to contribute to ExCALIBUR tests

You are welcome to contribute new application benchmarks and new systems part of
the ExCALIBUR benchmarking effort.

## Adding new systems

We need the [ReFrame](https://reframe-hpc.readthedocs.io/en/stable/)
configuration and a Spack environment for the system.

### ReFrame configuration

Add a new system to the ReFrame configuration in
[`benchmarks/reframe_config.py`](./benchmarks/reframe_config.py).  Read [ReFrame documentation about
configuration](https://reframe-hpc.readthedocs.io/en/stable/configure.html) for
more details, or see the examples of the existing systems.  Note: you likely do
not need to customise the programming environment in ReFrame, as we will use
Spack as build system, which will deal with that.

If available, the command `lscpu`, run on a compute node, is typically useful to
get information about the CPUs, to be used in the `processor` item of the system
configuration.  The numbers you need to watch out for are:

* "CPU(s)", (`num_cpus` in ReFrame configuration),
* "Thread(s) per core", (`num_cpus_per_core`),
* "Socket(s)", (`num_sockets`),
* "Core(s) per socket", (`num_cpus_per_socket`).

### Spack configuration

When using Spack as build system, ReFrame needs a [Spack
environment](https://spack.readthedocs.io/en/latest/environments.html) to run
its tests.  We provide already configured Spack environments in the
[`benchmarks/spack`](./benchmarks/spack) directory, for each system in the
ReFrame configuration.

Here are the steps to create a Spack environment for a new system:

* create the environment:
  ```
  spack env create --without-view -d spack/SYSTEM-NAME
  ```
  where `SYSTEM-NAME` is the same name as the ReFrame system name.  Remember to
  [disable
  views](https://spack.readthedocs.io/en/latest/environments.html#filesystem-views)
  with `--without-view` to avoid conflicts when installing incompatible packages
  in the same environment
* activate it:
  ```
  spack env activate -d spack/SYSTEM-NAME
  ```
* set the
  [`install_tree`](https://spack.readthedocs.io/en/latest/config_yaml.html#install-tree):
  ```
  spack config add 'config:install_tree:root:$env/opt/spack'
  ```
* make sure the compilers you want to add are in the `PATH` (e.g., load the
  relevant modules), then add them to the Spack environment with:
  ```
  spack compiler find
  ```
* add other packages (e.g., MPI): make sure the package you want to add are
  "visible" (e.g., load the relevant modules) and add them to the environment
  with
  ```
  spack external find PACKAGE-NAME ...
  ```
  where `PACKAGE-NAME ...` are the names of the corresponding Spack packages
* manually tweak the environment as necessary.  For example, if there is already
  a global Spack available in the system, you can [include its configuration
  files](https://spack.readthedocs.io/en/latest/environments.html#included-configurations),
  or [add its install trees as
  upstreams](https://spack.readthedocs.io/en/latest/chain.html).
  
* If you are using a custom repo for spack package recipes (see *Spack package* below), add
  it to the spack environment with
  ```
  spack -e /path/to/environment repo add /path/to/repo
  ```

## Adding new benchmarks

### Spack package

Before adding a new benchmark, make sure the application is available in
[Spack](https://spack.readthedocs.io/en/latest/package_list.html).  If it is
not, you can read the [Spack Package Creation
Tutorial](https://spack-tutorial.readthedocs.io/en/latest/tutorial_packaging.html)
to contribute a new recipe to build the application.

While we encourage users to contribute all Spack recipes upstream, we have a custom 
repo for packages not yet ready to be contributed to the main Spack repository.
This is in the `spack/repo` directory, create a subdirectory inside `spack/repo/packages` 
with the name of the package you want to add, and place into it the `package.py` Spack recipe.
On supported HPC systems, this repo is automatically added to the provided Spack environments.

### ReFrame benchmark

New benchmarks should be added in the `apps/` directory, under the specific
application subdirectory.  Please, add also a `README.md` file explaining what
the application does and how to run the benchmarks.

For writing ReFrame benchmarks you can read the documentation, in particular

* [ReFrame Tutorials](https://reframe-hpc.readthedocs.io/en/stable/tutorials.html)
* [Regression Test API](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html)

but you can also have a look at the sample file in
[`benchmarks/examples/sombrero/sombrero.py`](./benchmarks/examples/sombrero/sombrero.py).

For GPU benchmarks you need to

* set [`valid_systems = ['+gpu']`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.valid_systems)
* set the [`num_gpus_per_node`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_gpus_per_node) attribute,
* and add the key `gpu` to the [`extra_resources`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.extra_resources) dictionary to request the appropriate number of GPUs.

For an example of a GPU benchmark take a look at [OpenMM](benchmarks/apps/openmm/openmm_rfm.py).
