---

<style>
.reveal {
  font-size: 30px;
}
</style>

# Using ReFrame for reproducible and portable performance benchmarking

In this tutorial you will set up the excalibur-tests benchmarking framework on a HPC system, build and run example benchmarks, create a new benchmark and explore benchmark data.

---

## Installing the Framework

----

### Set up python environment

{!tutorial/setup-python.md!}

---


### Change to work directory

=== "Cosma"

	Move on to the next step.

=== "ARCHER2"

	On ARCHER2, the compute nodes do not have access to your home directory, therefore it is important to install everything in a [work file system](https://docs.archer2.ac.uk/user-guide/data/#work-file-systems). 
	Change to the work directory with

	```bash
	cd /work/ta131/ta131/${USER}
	```

	If you are tempted to use a symlink here, ensure you use `cd -P` when changing directory. 
	ARCHER2 compute nodes cannot read from `/home`, only `/work`, so not completely following symlinks can result in a broken installation.

----

### Clone the git repository

In the work directory, clone the [excalibur-tests](https://github.com/ukri-excalibur/excalibur-tests) repository with

```bash
git clone https://github.com/ukri-excalibur/excalibur-tests.git
```

----

### Create a virtual environment
Before proceeding to install the software, we recommend creating a python virtual environment to avoid clashes with other installed python packages. You can do this with
```bash
python3 -m venv excalibur-env
source excalibur-env/bin/activate
```

You should now see the name of the environment in parenthesis your terminal prompt, for example:
```bash
(excalibur-env) tk-d193@ln03:/work/d193/d193/tk-d193>
```

You will have to activate the environment each time you login. To deactivate the environment run `deactivate`.

----

### Install the excalibur-tests framework
Now we can use `pip` to install the package in the virtual environment. Update pip to the latest version with 
```bash
pip install --upgrade pip
```
then install the framework with
```bash
pip install -e ./excalibur-tests[post-processing]
```
We used the `editable` flag `-e` because later in the tutorial you will edit the repository to develop a new benchmark.

We included optional dependencies with `[post-processing]`. We will need those in the postprocessing section.

----

### Set configuration variables

Configure the framework by setting these environment variables

```bash
export RFM_CONFIG_FILES="$(pwd)/excalibur-tests/benchmarks/reframe_config.py"
export RFM_USE_LOGIN_SHELL="true"
```

----

### Install and configure spack

Finally, we need to install the `spack` package manager. The framework will use it to build the benchmarks. Clone spack with

```bash
git clone -c feature.manyFiles=true https://github.com/spack/spack.git
```

Then configure `spack` with

```bash
source ./spack/share/spack/setup-env.sh
```

Spack should now be in the default search path.

----

### Check installation was successful

You can check everything has been installed successfully by checking that `spack` and `reframe` are in path and the path to the ReFrame config file is set correctly

```bash
$ spack --version
0.22.0.dev0 (88e738c34346031ce875fdd510dd2251aa63dad7)
$ reframe --version
4.4.1
$ ls $RFM_CONFIG_FILES
/work/d193/d193/tk-d193/excalibur-tests/benchmarks/reframe_config.py
```

---

### Environment summary

If you log out and back in, you will have to run some of the above commands again to recreate your environment. These are (from your `work` directory):


=== "ARCHER2"
	```bash
	module load cray-python
	source excalibur-env/bin/activate
	export RFM_CONFIG_FILES="$(pwd)/excalibur-tests/benchmarks/reframe_config.py"
	export RFM_USE_LOGIN_SHELL="true"
	source ./spack/share/spack/setup-env.sh
	```

----

## Run Sombrero Example

You can now use ReFrame to run benchmarks from the `benchmarks/examples` and `benchmarks/apps` directories. The basic syntax is 
```bash
reframe -c <path/to/benchmark> -r
```

----

### system specific flags


=== "ARCHER2"
	In addition, on ARCHER2, you have to provide the quality of service (QoS) type for your job to ReFrame on the command line with `-J`. Use the "short" QoS to run the sombrero example with
	```bash
	reframe -c excalibur-tests/benchmarks/examples/sombrero -r -J'--qos=short'
	```
	You may notice you actually ran four benchmarks with that single command! That is because the benchmark is parametrized. We will talk about this in the next section.

----

### Output sample

=== "ARCHER2"
	```bash
	$ reframe -c benchmarks/examples/sombrero/ -r -J'--qos=short' --performance-report
	[ReFrame Setup]
	  version:           4.3.0
	  command:           '/mnt/lustre/a2fs-work3/work/d193/d193/tk-d193/excalibur-env/bin/reframe -c benchmarks/examples/sombrero/ -r -J--qos=short'
	  launched by:       tk-d193@ln03
	  working directory: '/mnt/lustre/a2fs-work3/work/d193/d193/tk-d193/excalibur-tests'
	  settings files:    '<builtin>', '/work/d193/d193/tk-d193/excalibur-tests/benchmarks/reframe_config.py'
	  check search path: '/mnt/lustre/a2fs-work3/work/d193/d193/tk-d193/excalibur-tests/benchmarks/examples/sombrero'
	  stage directory:   '/mnt/lustre/a2fs-work3/work/d193/d193/tk-d193/excalibur-tests/stage'
	  output directory:  '/mnt/lustre/a2fs-work3/work/d193/d193/tk-d193/excalibur-tests/output'
	  log files:         '/tmp/rfm-u1l6yt7f.log'
	  
	[==========] Running 4 check(s)
	[==========] Started on Fri Jul  7 15:47:45 2023 
	
	[----------] start processing checks
	[ RUN      ] SombreroBenchmark %tasks=2 %cpus_per_task=2 /de04c10b @archer2:compute-node+default
	[ RUN      ] SombreroBenchmark %tasks=2 %cpus_per_task=1 /c52a123d @archer2:compute-node+default
	[ RUN      ] SombreroBenchmark %tasks=1 %cpus_per_task=2 /c1c3a3f1 @archer2:compute-node+default
	[ RUN      ] SombreroBenchmark %tasks=1 %cpus_per_task=1 /52e1ce98 @archer2:compute-node+default
	[       OK ] (1/4) SombreroBenchmark %tasks=1 %cpus_per_task=2 /c1c3a3f1 @archer2:compute-node+default
	P: flops: 0.67 Gflops/seconds (r:1.2, l:None, u:None)
	[       OK ] (2/4) SombreroBenchmark %tasks=1 %cpus_per_task=1 /52e1ce98 @archer2:compute-node+default
	P: flops: 0.67 Gflops/seconds (r:1.2, l:None, u:None)
	[       OK ] (3/4) SombreroBenchmark %tasks=2 %cpus_per_task=2 /de04c10b @archer2:compute-node+default
	P: flops: 1.27 Gflops/seconds (r:1.2, l:None, u:None)
	[       OK ] (4/4) SombreroBenchmark %tasks=2 %cpus_per_task=1 /c52a123d @archer2:compute-node+default
	P: flops: 1.24 Gflops/seconds (r:1.2, l:None, u:None)
	[----------] all spawned checks have finished
	
	[  PASSED  ] Ran 4/4 test case(s) from 4 check(s) (0 failure(s), 0 skipped, 0 aborted)
	[==========] Finished on Fri Jul  7 15:48:23 2023 
	Log file(s) saved in '/tmp/rfm-u1l6yt7f.log'
	```

----

### Benchmark output

You can find build and run logs in the `output/` directory of a successful benchmark. They record how the benchmark was built by spack and ran by ReFrame.

While the benchmark is running, the log files are kept in the `stage/` directory. They remain there if the benchmark fails to build or run.

You can find the performance log file from the benchmark in `perflogs/`. The perflog records the captured figures of merit, environment variables and metadata about the job.

---

## Create a Benchmark

In this section you will create a ReFrame benchmark by writing a python class that tells ReFrame how to build and run an application and collect data from its output. 

For simplicity, we use the [`STREAM`](https://www.cs.virginia.edu/stream/ref.html) benchmark. It is a simple memory bandwidth benchmark with minimal build dependencies.

If you've already gone through the [ReFrame tutorial](reframe_tutorial.md) some of the steps in creating the STREAM benchmark are repeated. However, pay attention to the [`Create a Test Class`](excalibur-tests_tutorial.md#create-a-test-class) and [`Add Build Recipe`](excalibur-tests_tutorial.md#add-build-recipe) steps.

----

### How ReFrame works

When ReFrame executes a test it runs a pipeline of the following stages

![](https://reframe-hpc.readthedocs.io/en/stable/_images/pipeline.svg)

You can customise the behaviour of each stage or add a hook before or after each of them.  For more details, read the [ReFrame pipeline documentation](https://reframe-hpc.readthedocs.io/en/stable/pipeline.html).

----

### Getting started

To get started, open an empty `.py` file where you will write the ReFrame class, e.g. `stream.py`. Save the file in a new directory e.g. `excalibur-tests/benchmarks/apps/stream`.

----

### Include ReFrame modules

The first thing you need is include a few modules from ReFrame. These should be available if the installation step was successful.

```python
import reframe as rfm
import reframe.utility.sanity as sn
```

----

### Create a Test Class

ReFrame has built-in support for the Spack package manager.
In the following we will use the custom class `SpackTest` we created for our `benchmarks` module, which provides a tighter integration with Spack and reduces the boilerplate code you'd otherwise have to include.

```python
from benchmarks.modules.utils import SpackTest

@rfm.simple_test
class StreamBenchmark(SpackTest):
```

The data members and methods detailed in the following sections should be placed inside this class.

----

### Add Build Recipe

We prefer installing packages via spack whenever possible. In this exercise, the spack package for `stream` already exists in the global spack repository.

The `SpackTest` base class takes care of setting up spack as the build system ReFrame uses. We only need to instruct ReFrame to install version `5.10` of the `stream` [spack package](https://spack.readthedocs.io/en/latest/package_list.html#stream) using the `openmp` variant.

```python
spack_spec = 'stream@5.10 +openmp'
```

Note that we did not specify a compiler. Spack will use a compiler from the spack environment. The complete spec is recorded in the build log.

----

### Add Run Configuration

The ReFrame class tells ReFrame where and how to run the benchmark. We want to run on one task on a full archer2 node using 128 OpenMP threads to use the full node.

```python
valid_systems = ['*']
valid_prog_environs = ['default']
executable = 'stream_c.exe'
num_tasks = 1
time_limit = '5m'
use_multithreading = False
```

----

### Add environment variables

Environment variables can be added to the `env_vars` attribute.

```python
env_vars['OMP_NUM_THREADS'] = f'{num_cpus_per_task}'
env_vars['OMP_PLACES'] = 'cores'
```

----

{!tutorial/stream-sanity-and-performance.md!}

----

### Run Stream Benchmark

You can now run the benchmark in the same way as the previous sombrero example

=== "ARCHER2"
	```bash
	reframe -c excalibur-tests/benchmarks/apps/stream/ -r --system archer2 -J'--qos=short'
	```

----

### Sample Output
=== "ARCHER2"
	```bash
	$ reframe -c excalibur-tests/benchmarks/examples/stream/ -r -J'--qos=short'
	[ReFrame Setup]
	  version:           4.4.1
	  command:           '/mnt/lustre/a2fs-work3/work/d193/d193/tk-d193/ciuk-demo/demo-env/bin/reframe -c excalibur-tests/benchmarks/examples/stream/ -r -J--qos=short'
	  launched by:       tk-d193@ln03
	  working directory: '/mnt/lustre/a2fs-work3/work/d193/d193/tk-d193/ciuk-demo'
	  settings files:    '<builtin>', '/work/d193/d193/tk-d193/ciuk-demo/excalibur-tests/benchmarks/reframe_config.py'
	  check search path: '/mnt/lustre/a2fs-work3/work/d193/d193/tk-d193/ciuk-demo/excalibur-tests/benchmarks/examples/stream'
	  stage directory:   '/mnt/lustre/a2fs-work3/work/d193/d193/tk-d193/ciuk-demo/stage'
	  output directory:  '/mnt/lustre/a2fs-work3/work/d193/d193/tk-d193/ciuk-demo/output'
	  log files:         '/tmp/rfm-z87x4min.log'
	
	  [==========] Running 1 check(s)
	  [==========] Started on Thu Nov 30 14:50:21 2023 
	  
	  [----------] start processing checks
	  [ RUN      ] StreamBenchmark /8aeff853 @archer2:compute-node+default
	  [       OK ] (1/1) StreamBenchmark /8aeff853 @archer2:compute-node+default
	  P: Copy: 1380840.8 MB/s (r:0, l:None, u:None)
	  P: Scale: 1369568.7 MB/s (r:0, l:None, u:None)
	  P: Add: 1548666.1 MB/s (r:0, l:None, u:None)
	  P: Triad: 1548666.1 MB/s (r:0, l:None, u:None)
	  [----------] all spawned checks have finished
	  
	  [  PASSED  ] Ran 1/1 test case(s) from 1 check(s) (0 failure(s), 0 skipped, 0 aborted)
	  [==========] Finished on Thu Nov 30 14:51:13 2023 
	  Log file(s) saved in '/tmp/rfm-z87x4min.log'
	```

----

### Interpreting STREAM results

With default compile options, STREAM uses arrays of 10 million elements. On a full node, the default array size fits into cache, and the benchmark does not report the correct memory bandwidth. 
Therefore the numbers from this tutorial are not comparable with other, published, results.

To avoid caching, increase the array size during build by adding e.g. `stream_array_size=64000000` to the spack spec. 

----

### Parametrized tests

You can pass a list to the `parameter()` built-in function in the class body to create a parametrized test. You cannot access the individual parameter value within the class body, so any reference to them should be placed in the appropriate function, for example `__init__()`

Example: Parametrize the array size

```python
array_size = parameter(int(i) for i in [4e6,8e6,16e6,32e6,64e6])
def __init__(self):
    self.spack_spec = f"stream@5.10 +openmp stream_array_size={self.array_size}"
```

=== "ARCHER2"
	```bash
	[----------] start processing checks
	[ RUN      ] StreamBenchmark %array_size=64000000 /bbfd0e71 @archer2:compute-node+default
	[ RUN      ] StreamBenchmark %array_size=32000000 /e16f9017 @archer2:compute-node+default
	[ RUN      ] StreamBenchmark %array_size=16000000 /abc01230 @archer2:compute-node+default
	[ RUN      ] StreamBenchmark %array_size=8000000 /51d83d77 @archer2:compute-node+default
	[ RUN      ] StreamBenchmark %array_size=4000000 /8399bc0b @archer2:compute-node+default
	[       OK ] (1/5) StreamBenchmark %array_size=32000000 /e16f9017 @archer2:compute-node+default
	P: Copy: 343432.5 MB/s (r:0, l:None, u:None)
	P: Scale: 291065.8 MB/s (r:0, l:None, u:None)
	P: Add: 275577.5 MB/s (r:0, l:None, u:None)
	P: Triad: 247425.0 MB/s (r:0, l:None, u:None)
	[       OK ] (2/5) StreamBenchmark %array_size=16000000 /abc01230 @archer2:compute-node+default
	P: Copy: 2538396.7 MB/s (r:0, l:None, u:None)
	P: Scale: 2349544.5 MB/s (r:0, l:None, u:None)
	P: Add: 2912500.4 MB/s (r:0, l:None, u:None)
	P: Triad: 2886402.8 MB/s (r:0, l:None, u:None)
	[       OK ] (3/5) StreamBenchmark %array_size=8000000 /51d83d77 @archer2:compute-node+default
	P: Copy: 1641807.1 MB/s (r:0, l:None, u:None)
	P: Scale: 1362616.5 MB/s (r:0, l:None, u:None)
	P: Add: 1959382.9 MB/s (r:0, l:None, u:None)
	P: Triad: 1940497.3 MB/s (r:0, l:None, u:None)
	[       OK ] (4/5) StreamBenchmark %array_size=64000000 /bbfd0e71 @archer2:compute-node+default
	P: Copy: 255622.4 MB/s (r:0, l:None, u:None)
	P: Scale: 235186.0 MB/s (r:0, l:None, u:None)
	P: Add: 204853.9 MB/s (r:0, l:None, u:None)
	P: Triad: 213072.2 MB/s (r:0, l:None, u:None)
	[       OK ] (5/5) StreamBenchmark %array_size=4000000 /8399bc0b @archer2:compute-node+default
	P: Copy: 1231355.3 MB/s (r:0, l:None, u:None)
	P: Scale: 1086783.2 MB/s (r:0, l:None, u:None)
	P: Add: 1519446.0 MB/s (r:0, l:None, u:None)
	P: Triad: 1548666.1 MB/s (r:0, l:None, u:None)
	[----------] all spawned checks have finished
	
	[  PASSED  ] Ran 5/5 test case(s) from 5 check(s) (0 failure(s), 0 skipped, 0 aborted)
	[==========] Finished on Thu Nov 30 14:34:48 2023 
	```

----

### Reference values

ReFrame can automate checking that the results fall within an expected range. We can use it in our previous example of increasing the array size to avoid caching. You can set a different reference value for each `perf_key` in the performance function. For example, set the test to fail if it falls outside of +-25% of the values obtained with the largest array size.

=== "ARCHER2"
	```python
    reference = {
        'archer2': {
            'Copy':  (260000, -0.25, 0.25, 'MB/s'),
            'Scale': (230000, -0.25, 0.25, 'MB/s'),
            'Add':   (210000, -0.25, 0.25, 'MB/s'),
            'Triad': (210000, -0.25, 0.25, 'MB/s')
        }
    }
	```

> The performance reference tuple consists of the reference value, the lower and upper thresholds expressed as fractional numbers relative to the reference value, and the unit of measurement. If any of the thresholds is not relevant, None may be used instead. Also, the units in this reference variable are entirely optional, since they were already provided through the @performance_function decorator.

----

## Useful Reading

----

### ReFrame

- [ReFrame Documentation](https://reframe-hpc.readthedocs.io/)
- ReFrame tutorials
    - [Tutorial 1: Getting started with ReFrame](https://reframe-hpc.readthedocs.io/en/stable/tutorial_basics.html)
    - [Tutorial 2: Customizing Further a Regression Test](https://reframe-hpc.readthedocs.io/en/stable/tutorial_advanced.html)
    - [Tutorial 3: Using Dependencies in ReFrame Tests](https://reframe-hpc.readthedocs.io/en/stable/tutorial_deps.html)
    - [Tutorial 4: Using Test Fixtures](https://reframe-hpc.readthedocs.io/en/stable/tutorial_fixtures.html)
    - [Tutorial 5: Using Build Automation Tools As a Build System](https://reframe-hpc.readthedocs.io/en/stable/tutorial_build_automation.html)
    - [Tutorial 6: Tips and Tricks](https://reframe-hpc.readthedocs.io/en/stable/tutorial_tips_tricks.html)
- Libraries of ReFrame tests
    - [Official ReFrame test library](https://reframe-hpc.readthedocs.io/en/stable/hpctestlib.html)
    - [ReFrame GitHub organisation with various contributed test libraries](https://github.com/reframe-hpc)

----

### Spack

- [Spack documentation](https://spack.readthedocs.io/)
- [Spack tutorial (including YouTube recordings)](https://spack-tutorial.readthedocs.io/)
- [Spack package searchable list](https://packages.spack.io/)

