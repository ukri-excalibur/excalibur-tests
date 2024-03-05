# How to contribute to ExCALIBUR tests

You are welcome to contribute new application benchmarks and new systems part of
the ExCALIBUR benchmarking effort. The easiest way to contribute is to open an
issue or a pull request to the repository.

## Adding new benchmarks

In particular, adding new benchmarks that are useful to the scientific community is
welcome!

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

but you can also have a look at the 
[sombrero example](https://github.com/ukri-excalibur/excalibur-tests/blob/main/benchmarks/examples/sombrero).

For GPU benchmarks you need to

* set [`valid_systems = ['+gpu']`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.valid_systems)
* set the [`num_gpus_per_node`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_gpus_per_node) attribute,
* and add the key `gpu` to the [`extra_resources`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.extra_resources) dictionary to request the appropriate number of GPUs.

For an example of a GPU benchmark take a look at [OpenMM](https://github.com/ukri-excalibur/excalibur-tests/tree/main/benchmarks/apps/openmm).
