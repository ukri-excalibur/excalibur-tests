# Automating benchmarks with ReFrame

## Outline

1. How ReFrame executes tests
2. Structure of a ReFrame test -- Hello world example
3. Configuring ReFrame to run tests on Cosma
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

## Set up environment

This tutorial was originally run on the [Cosma](https://cosma.readthedocs.io/en/latest/) supercomputer. It should be straightforward to run on a different platform, the requirements are  `gcc`, `git` and `python3`. (for the later parts you also need `make`, `autotools`, `cmake` and `spack`).
Before proceeding to install ReFrame, we recommend creating a python virtual environment to avoid clashes with other installed python packages. First load a newer python module.

```bash
module swap python/3.10.12
```

Then create an environment and activate it with

```bash
python3 -m venv reframe_tutorial
source reframe_tutorial/bin/activate
```

You will have to activate the environment each time you login. To deactivate the environment run `deactivate`.

----

## Install ReFrame

Then install ReFrame with `pip`. I am installing version `4.5.2` because we will follow tutorials that have been changed in the latest `4.6.0` version.

```bash
pip install reframe-hpc==4.5.2
```

Alternatively, you can

```bash
git clone -q --depth 1 --branch v4.5.2 https://github.com/reframe-hpc/reframe.git
source reframe/bootstrap.sh
```

The ReFrame git repository also contains the source code of the ReFrame tutorials. It is recommended to run the git clone step, even if you used `pip install` to install ReFrame. We will refer to the tutorial solutions later.

---

## Hello world example

[Hello world example](https://reframe-hpc.readthedocs.io/en/v4.5.2/tutorial_basics.html#the-hello-world-test)

----

### Include ReFrame modules

The first thing you need is include a few modules from ReFrame. These should be available if the installation step was successful.

```python
import reframe as rfm
import reframe.utility.sanity as sn
```

----

### Create a Test Class

- ReFrame uses decorators to mark classes as tests. 
- This marks `class HelloTest` as a `rfm.simple_test`.
- ReFrame tests ultimately derive from `RegressionTest`. There are other derived classes such as `RunOnlyRegressionTest`, we get to those later.

```python

@rfm.simple_test
class HelloTest(rfm.RegressionTest):
```

- The data members and methods detailed in the following sections should be placed inside this class.

----

### Add mandatory attributes

- `valid_systems` for where this test can run
- `valid_prog_environs` for what compilers this test can build with. More on it later.
- `sourcepath` for source file in a single source test. More on build systems later.
- Could add `sourcesdir` but it defaults to `src/`

```python
    valid_systems = ['*']
    valid_prog_environs = ['*']
    sourcepath = 'hello.c'
```

----

### Add sanity check

- ReFrame, by default, makes no assumption about whether a test is successful or not.
- A test must provide a validation function
- ReFrame provides a rich set of utility functions that help matching patterns and extract values from the test’s output
- Here we match a string from stdout

```python
    @sanity_function
    def assert_hello(self):
        return sn.assert_found(r'Hello, World\!', self.stdout)
```

----

## Builtin programming environment

- `reframe --show-config`
- Builtin programming environment uses `cc` to compile

---

## Configuring ReFrame for HPC systems (Cosma)
> In ReFrame, all the details of the various interactions of a test with the system environment are handled transparently and are set up in its configuration file.
- [Configuration](https://reframe-hpc.readthedocs.io/en/v4.5.2/tutorial_basics.html#more-of-hello-world)
  - Set accounting parameters with
    - `'access': ['--partition=bluefield1', '--account=do009'],`
  - Create at least one programming environment to set compilers
    - `-p` flag filters tests by programming environment
  - Scheduler to run on compute nodes
    - Add `time_limit = 1m` to ReFrame tests to run on Cosma
    - Set from command line with `-S time_limit='1m'`

----

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

---

## Performance tests

Performance tests capture data in performance variables. For simplicity, we use the [STREAM benchmark](https://github.com/jeffhammond/STREAM) as an example. It is the de facto memory bandwidth benchmark.

To record the performance of the benchmark, ReFrame should extract a figure of merit from the output of the test. A function decorated with the `@performance_function` decorator extracts or computes a performance metric from the test’s output.

----

### Boilerplate

Same as before. We can now specify valid systems and prog environments

```python
import reframe as rfm
import reframe.utility.sanity as sn

@rfm.simple_test
class StreamTest(rfm.RegressionTest):
    valid_systems = ['cosma']
    valid_prog_environs = ['gnu', 'intel']
```

----

### Git Cloning the source

we can retrieve specifically a Git repository by assigning its URL directly to the sourcesdir attribute:

```python
    sourcesdir='https://github.com/jeffhammond/STREAM'
```

----

### Environment variables

We can set environment variables by defining the `env_vars` attribute

```python
    env_vars = {
        'OMP_NUM_THREADS': '4',
        'OMP_PLACES': 'cores'
    }
```

----

### Building

- Remember the pipeline ReFrame executes. We can run arbitrary functions in the pipeline by decorating them with `@run_before` or `@run_after`
- Here we can insert compiler flags before compiling

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

### Sanity function

Similar to before, we can check a line in stdout for validation.

```python
     @sanity_function
     def validate_solution(self):
        return sn.assert_found(r'Solution Validates', self.stdout)
```

----

## Add Performance Pattern Check

To record the performance of the benchmark, ReFrame should extract a figure of merit from the output of the test. A function decorated with the `@performance_function` decorator extracts or computes a performance metric from the test’s output.

> In this example, we extract four performance variables, namely the memory bandwidth values for each of the “Copy”, “Scale”, “Add” and “Triad” sub-benchmarks of STREAM, where each of the performance functions use the [`extractsingle()`](https://reframe-hpc.readthedocs.io/en/latest/deferrable_functions_reference.html#reframe.utility.sanity.extractsingle) utility function. For each of the sub-benchmarks we extract the “Best Rate MB/s” column of the output (see below) and we convert that to a float.

----

## Performance Pattern Check

```python
@performance_function('MB/s', perf_key='Copy')
def extract_copy_perf(self):
    return sn.extractsingle(r'Copy:\s+(\S+)\s+.*', self.stdout, 1, float)

@performance_function('MB/s', perf_key='Scale')
def extract_scale_perf(self):
    return sn.extractsingle(r'Scale:\s+(\S+)\s+.*', self.stdout, 1, float)

@performance_function('MB/s', perf_key='Add')
def extract_add_perf(self):
    return sn.extractsingle(r'Add:\s+(\S+)\s+.*', self.stdout, 1, float)

@performance_function('MB/s', perf_key='Triad')
def extract_triad_perf(self):
    return sn.extractsingle(r'Triad:\s+(\S+)\s+.*', self.stdout, 1, float)
```

----

### Perflogs

- Perflogs are output in `perflogs/<system>/<partition>`
- By default a lot of information is printed. This can be customized in the configuration file. More on this later.
- By default not much information about build step, has to be linked back to build environment
- See `.reframe/reports/` or use `--report-file`

----

## Reference values

ReFrame can automate checking that the results fall within an expected range. You can set a different reference value for each `perf_key` in the performance function. For example, set the test to fail if it falls outside of +-25% of the values obtained with the previous array size.

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
- [Build systems Reference](https://reframe-hpc.readthedocs.io/en/v4.5.2/regression_test_api.html#build-systems)

----

### [Make](https://reframe-hpc.readthedocs.io/en/v4.5.2/tutorial_advanced.html#more-on-building-tests) 

- Tutorial in `tutorials/advanced/makefiles/maketest.py`. 

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
- Tutorial in `tutorials/build_systems/spack/spack_test.py`
- In `rfm_job.out` you can see that it
    - Creates a blank environment
    - Builds all dependencies -- takes quite long
- `excalibur-tests` provides utilities and settings for Spack builds in ReFrame. See the [Next Tutorial](../archer2_tutorial) for details.

---

## Run-only tests
- Tutorial in `tutorials/advanced/runonly/echorand.py`
