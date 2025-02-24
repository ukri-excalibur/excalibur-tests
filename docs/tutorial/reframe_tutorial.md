# Automating benchmarks with ReFrame

## Outline

1. How ReFrame executes tests
2. Structure of a ReFrame test -- Hello world example
3. Configuring ReFrame to run tests on HPC systems
4. Writing performance tests -- Stream example
5. Working with build systems -- Make, CMake, Autotools, Spack examples
6. Avoiding build systems -- Run-only tests

This tutorial is adapted from [ReFrame 4.5 tutorials](https://reframe-hpc.readthedocs.io/en/v4.5.2/tutorials.html), that also cover more ReFrame features. Direct quotes from the tutorial are marked with

> ReFrame Tutorials

There's a [new tutorial](https://reframe-hpc.readthedocs.io/en/v4.6.0/tutorial.html) with a slightly different approach in ReFrame 4.6.

---

## How ReFrame executes tests

When ReFrame executes a test it runs a pipeline of the following stages

![](https://reframe-hpc.readthedocs.io/en/stable/_images/pipeline.svg)

You can customise the behaviour of each stage or add a hook before or after each of them.  For more details, read the [ReFrame pipeline documentation](https://reframe-hpc.readthedocs.io/en/stable/pipeline.html).

---

## Set up python environment

{!tutorial/setup-python.md!}

----

## Install ReFrame

Then install ReFrame with `pip`.

```bash
pip install reframe-hpc
```

Alternatively, you can

```bash
git clone -q --depth 1 --branch v4.5.2 https://github.com/reframe-hpc/reframe.git
source reframe/bootstrap.sh
```

You can also clone the ReFrame git repository to get the source code of the ReFrame tutorials.
We will refer to some of the tutorial solutions later.
ReFrame rewrote their tutorials in v4.6 and some of the examples we are using are not there anymore,
therefore it's best to clone ReFrame v4.5.

---

## Hello world example

There's a [Hello world example](https://reframe-hpc.readthedocs.io/en/v4.5.2/tutorial_basics.html#the-hello-world-test) in the ReFrame 4.5 tutorial that explains how to create a simple ReFrame test.

ReFrame tests are python classes that describe how a test is run.
To get started, open an empty `.py` file where you will write the ReFrame class, e.g. `hello.py`.

----

### Include ReFrame module

The first thing you need is to include ReFrame.
We separately import sanity to simplify the syntax.
These should be available if the installation step was successful.

```python
import reframe as rfm
import reframe.utility.sanity as sn
```

----

### Create a Test Class

ReFrame uses decorators to mark classes as tests.
This marks `class HelloTest` as a `rfm.simple_test`.
ReFrame tests ultimately derive from `RegressionTest`.
There are other derived classes such as `RunOnlyRegressionTest`, we get to those later.

```python

@rfm.simple_test
class HelloTest(rfm.RegressionTest):
```

The data members and methods detailed in the following sections should be placed inside this class.

----

### Add mandatory attributes

- `valid_systems` for where this test can run. For now we haven't defined any systems so we leave it as `'*'` (any system)
- `valid_prog_environs` for what compilers this test can build with. More on it later.
- In a test with a single source file, it is enough to define `sourcepath`. More on build systems later.
- We could add `sourcesdir` to point to the source directory, but it defaults to `src/`

```python
    valid_systems = ['*']
    valid_prog_environs = ['*']
    sourcepath = 'hello.c'
```

----

### Add sanity check

- ReFrame, by default, makes no assumption about whether a test is successful or not.
- A test must provide a validation function that asserts whether the test was successful
- ReFrame provides utility functions that help matching patterns and extract values from the test’s output
- Here we match a string from stdout

```python
    @sanity_function
    def assert_hello(self):
        return sn.assert_found(r'Hello, World\!', self.stdout)
```

### Run the benchmark

The basic syntax to run ReFrame benchmarks is

```bash
reframe -c path/to/benchmark -r
```

----

## Builtin programming environment

We didn't tell reframe anything about how to compile the hello world example. How did it compile?
ReFrame uses a buitin programming environment by default.
You can see this with `reframe --show-config`
The builtin programming environment only contains the `cc` compiler,
compiling a C++ or Fortran code will fail

---

## Configuring ReFrame for HPC systems
> In ReFrame, all the details of the various interactions of a test with the system environment are handled transparently and are set up in its [configuration file](https://reframe-hpc.readthedocs.io/en/v4.5.2/tutorial_basics.html#more-of-hello-world).

For the minimum configuration to run jobs on the system we need to

=== "Cosma"

    - Create a system with a name and a description
    - Set the module system for accessing centrally installed modules
    - Create a compute node partition
      - Set a scheduler and a MPI launcher to run on compute nodes
        - On Cosma, the scheduler rejects jobs that don't set a time limit. Add `time_limit = 1m` to ReFrame tests to run on Cosma or set from command line with `-S time_limit='1m'`
      - Set access options
	```
	'access': ['--partition=bluefield1', '--account=do009'],
	```
    - Create at least one programming environment to set compilers

	```python
    site_configuration = {
        'systems' : [
            {
                'name': 'cosma',
                'descr': 'Cosma for performance workshop',
                'hostnames': ['login[0-9][a-z].pri.cosma[0-9].alces.network'],
                'modules_system': 'tmod4',
                'partitions': [
                    {
                        'name': 'compute-node',
                        'scheduler': 'slurm',
                        'launcher': 'mpiexec',
                        'environs': ['gnu'],
                        'access': ['--partition=bluefield1', '--account=do009'],
                    }
                ]
            }
        ],
        'environments': [
            {
                'name': 'gnu',
                'modules': ['gnu_comp', 'openmpi'],
                'cc': 'mpicc',
                'cxx': 'mpic++',
                'ftn': 'mpif90'
            },
        ]
    }
	```

=== "ARCHER2"

	- Create a system with a name and a description
	- Set the module system for accessing centrally installed modules
	- Create a compute node partition
	  - Set a scheduler and a MPI launcher to run on compute nodes
	  - Set access options with 
    ```
	'access': ['--partition=standard', '--qos=short'],
	```
	- Create at least one programming environment to set compilers

    ```python
    site_configuration = {
        'systems' : [
            {
                'name': 'archer2',
                'descr': 'ARCHER2 config for CIUK workshop',
                'hostnames': ['ln[0-9]+'],
                'partitions': [
                    {
                        'name': 'compute-node',
                        'scheduler': 'slurm',
                        'launcher': 'srun',
                        'access': ['--partition=standard', '--qos=short'],
                        'environs': ['cray'],
                    }
                ]
            }
        ],
        'environments': [
            {
                'name': 'cray',
                'cc': 'mpicc',
                'cxx': 'mpic++',
                'ftn': 'mpif90'
            },
        ]
    }
	```

---

## Performance tests

Performance tests capture data in performance variables. For simplicity, we use the [STREAM benchmark](https://github.com/jeffhammond/STREAM) as an example. It is the de facto memory bandwidth benchmark. It has four kernels that stream arrays from memory and
perform different floating point operations on them.
- Copy: `A = B`
- Scale: `C = a * B`
- Add: `C = A + B`
- Triad: `C = a * A + B`

----

### Create the Test Class

The imports and the class declaration look the same as in the hello world example. 
We can now specify valid systems and programming environments to run on the system we just configured. 
You can adapt these to your system, or keep using `'*'` to run on any platform.


=== "Cosma"
	```python
    import reframe as rfm
    import reframe.utility.sanity as sn

    @rfm.simple_test
    class StreamTest(rfm.RegressionTest):
        valid_systems = ['cosma']
        valid_prog_environs = ['gnu']
	```
	
=== "ARCHER2"

	```python
    import reframe as rfm
    import reframe.utility.sanity as sn

    @rfm.simple_test
    class StreamTest(rfm.RegressionTest):
        valid_systems = ['archer2']
        valid_prog_environs = ['cray']
	```

----

### Git Cloning the source

We can retrieve specifically a Git repository by assigning its URL directly to the sourcesdir attribute:

```python
    sourcesdir='https://github.com/jeffhammond/STREAM'
```

----

### Environment variables

We can set environment variables in the `env_vars` dictionary.

```python
    self.env_vars['OMP_NUM_THREADS'] = 4
    self.env_vars['OMP_PLACES'] = 'cores'
```

----

### Building the STREAM benchmark

Recall the pipeline ReFrame executes when running a test. 
We can insert arbitrary functions between any steps in in the pipeline by decorating them with `@run_before` or `@run_after`
Here we can set compiler flags before compiling.
The STREAM benchmark takes the array size as a compile time argument. 
It should be large enough to overflow all levels of cache so that there is no data reuse and we measure the main memory bandwidth.

```python
    build_system='SingleSource'
    sourcepath='stream.c'
    arraysize = 2**20

    @run_before('compile')
    def set_compiler_flags(self):
        self.build_system.cppflags = [f'-DSTREAM_ARRAY_SIZE={self.arraysize}']
        self.build_system.cflags = ['-fopenmp', '-O3']
```

----

{!tutorial/stream-sanity-and-performance.md!}

----

### Perflogs

The output from performance tests is written in perflogs. They are csv files that are appended each time a test is ran. By default the perflogs are output in `perflogs/<system>/<partition>`. By default a lot of information about the test is stored. This can be customized in the configuration file.
By default there is not much information about build step, but ReFrame will provide a link back to build environment. A more verbose report is written in `.reframe/reports/`, you can use the `--report-file` option to direct the report to a different file.

`excalibur-tests` provides tools to read and process the perflogs. See the [Next Tutorial](excalibur-tests_tutorial.md) for details.

----

## Reference values

ReFrame can automate checking that the results fall within an expected range. You can set a different reference value for each `perf_key` in the performance function. For example, set the test to fail if it falls outside of +-25% of the values obtained with the previous array size.


=== "Cosma"
	```python
    reference = {
        'cosma': {
            'Copy':  (40000, -0.25, 0.25, 'MB/s'),
            'Scale': (20000, -0.25, 0.25, 'MB/s'),
            'Add':   (20000, -0.25, 0.25, 'MB/s'),
            'Triad': (20000, -0.25, 0.25, 'MB/s')
        }
    }
	```

=== "Archer2"
	```python
    reference = {
        'archer2': {
            'Copy':  (260000, -0.25, 0.25, 'MB/s'),
            'Scale': (200000, -0.25, 0.25, 'MB/s'),
            'Add':   (200000, -0.25, 0.25, 'MB/s'),
            'Triad': (200000, -0.25, 0.25, 'MB/s')
        }
    }
	```

> The performance reference tuple consists of the reference value, the lower and upper thresholds expressed as fractional numbers relative to the reference value, and the unit of measurement. If any of the thresholds is not relevant, None may be used instead. Also, the units in this reference variable are entirely optional, since they were already provided through the @performance_function decorator.


----

## Parametrized tests

You can pass a list to the `parameter()` built-in function in the class body to create a parametrized test. You cannot access the individual parameter value within the class body, so any reference to them should be placed in the appropriate function, for example `__init__()`

For parametrisation you can add for example
```python
    arraysize = parameter([5,15,25])
    self.build_system.cppflags = [f'-DSTREAM_ARRAY_SIZE=$((2 ** {self.arraysize}))']
```

You can have multiple parameters. ReFrame will run all parameter combinations by default.

---

## [Build systems](https://reframe-hpc.readthedocs.io/en/v4.5.2/tutorial_advanced.html#more-on-building-tests)

ReFrame supports many commonly used build systems, include Cmake, Autotools, Spack and Easybuild. See the
[Build systems Reference](https://reframe-hpc.readthedocs.io/en/v4.5.2/regression_test_api.html#build-systems) for details.
Here we show a few examples.

----

### [Make](https://reframe-hpc.readthedocs.io/en/v4.5.2/tutorial_advanced.html#more-on-building-tests)

- [Tutorial in `tutorials/advanced/makefiles/maketest.py`.](https://reframe-hpc.readthedocs.io/en/v4.5.2/tutorial_advanced.html#more-on-building-tests)

> First, if you’re using any build system other than SingleSource, you must set the executable attribute of the test, because ReFrame cannot know what is the actual executable to be run. We then set the build system to Make and set the preprocessor flags as we would do with the SingleSource build system.

----

### [Autotools](https://reframe-hpc.readthedocs.io/en/v4.5.2/tutorial_advanced.html#adding-a-configuration-step-before-compiling-the-code)
> It is often the case that a configuration step is needed before compiling a code with make. To address this kind of projects, ReFrame aims to offer specific abstractions for “configure-make” style of build systems. It supports CMake-based projects through the CMake build system, as well as Autotools-based projects through the Autotools build system.

- [Automake Hello example](https://github.com/ntegan/amhello)

```python
import reframe as rfm
import reframe.utility.sanity as sn

@rfm.simple_test
class AutoHelloTest(rfm.RegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['*']
    sourcesdir = 'https://github.com/ntegan/amhello.git'
    build_system = 'Autotools'
    executable = './src/hello'
    prebuild_cmds = ['autoreconf --install .']
    time_limit = '5m'

    @sanity_function
    def assert_hello(self):
        return sn.assert_found(r'Hello world\!', self.stdout)
```

----

### [CMake](https://reframe-hpc.readthedocs.io/en/v4.5.2/regression_test_api.html#reframe.core.buildsystems.CMake)
- [CMake Hello example](https://github.com/jameskbride/cmake-hello-world)

```python
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class CMakeHelloTest(rfm.RegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['*']
    sourcesdir = 'https://github.com/jameskbride/cmake-hello-world.git'
    build_system = 'CMake'
    executable = './CMakeHelloWorld'
    time_limit = '5m'

    @sanity_function
    def assert_hello(self):
        return sn.assert_found(r'Hello, world\!', self.stdout)

```

----

### [Spack](https://reframe-hpc.readthedocs.io/en/v4.5.2/regression_test_api.html#reframe.core.buildsystems.Spack)

- ReFrame will use a user-provided Spack environment in order to build and test a set of specs.
- [Tutorial in `tutorials/build_systems/spack/spack_test.py`](https://reframe-hpc.readthedocs.io/en/v4.5.2/tutorial_build_automation.html#using-spack-to-build-the-test-code)
- In `rfm_job.out` you can see that it
    - Creates a blank environment
    - Builds all dependencies -- takes quite long
- `excalibur-tests` provides utilities and settings for Spack builds in ReFrame. See the [Next Tutorial](excalibur-tests_tutorial.md) for details.

---

## Run-only tests

If you don't wish to build your application in ReFrame (we recommend that you do!), you can define a run-only test.
Run-only tests derive from the `rfm.RunOnlyRegressionTest` class instead of `rfm.RegressionTest`.
Instead of a build system, you define an executable which reframe expects to find in `$PATH`.
See [tutorial in `tutorials/advanced/runonly/echorand.py`](https://reframe-hpc.readthedocs.io/en/v4.5.2/tutorial_advanced.html#writing-a-run-only-regression-test)
