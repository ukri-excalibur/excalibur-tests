---
#type: slide
---

<style>
.reveal {
  font-size: 30px;
}
</style>

# Benchmarking Tutorial

In this tutorial you will set up the benchmarking framework on the [ARCHER2](https://www.archer2.ac.uk) supercomputer, build and run example benchmarks, create a new benchmark and explore benchmark data.

## Collaborative document for RSECon23

[hackmd link](https://hackmd.io/@BvcZAzBNTSazzlAasCy2nw/rJsG3X0ah)

---

# Getting Started

To complete this tutorial, you need to [connect to ARCHER2 via ssh](https://docs.archer2.ac.uk/user-guide/connecting/). You will need

1. An ARCHER2 account. You can [request a new account](https://docs.archer2.ac.uk/quick-start/quickstart-users/#request-an-account-on-archer2) if you haven't got one you can use. Use the project code `ta122` to request your account. You can use an existing ARCHER2 account to complete this workshop.
2. A command line terminal with an ssh client. Most Linux and Mac systems come with these preinstalled. Please see [Connecting to ARCHER2](https://docs.archer2.ac.uk/user-guide/connecting/#command-line-terminal) for more information and Windows instructions.

----

Once you have the above prerequisites, you have to [generate an ssh key pair](https://docs.archer2.ac.uk/user-guide/connecting/#ssh-key-pairs) and [upload the public key to SAFE](https://docs.archer2.ac.uk/user-guide/connecting/#upload-public-part-of-key-pair-to-safe). 

When you are done, check that you are able to connect to ARCHER2 with

```bash
ssh username@login.archer2.ac.uk
```

---

# Installing the Framework

----

## Set up python

We are going to use `python` and the `pip` package installer to install and run the framework. Load the `cray-python` module to get a python version that fills the requirements.
```bash
$ module load cray-python
```
You can check with `python3 --version` that your python version is `3.8` or greater. **[JQ - `python` also works]** You will have to load this module every time you login.

(at the time of writing, the default version was `3.9.13`).

----

## Change to work directory

On ARCHER2, the compute nodes do not have access to your home directory, therefore it is important to install everything in a [work file system](https://docs.archer2.ac.uk/user-guide/data/#work-file-systems). Change to the work directory with

```bash
$ cd /work/ta122/ta122/${USER}
```

:::warning
If you are tempted to use a symlink here, ensure you use `cd -P` when changing directory. Archer2 compute nodes cannot read from `/home`, only `/work`, so not completely following symlinks can result in a broken installation.
:::

----

## Clone the framework repository

In the work directory, clone the [excalibur-tests](https://github.com/ukri-excalibur/excalibur-tests) repository with

```bash
$ git clone https://github.com/ukri-excalibur/excalibur-tests.git
```

----

## Create a virtual environment
Before proceeding to install the software, we recommend creating a python virtual environment to avoid clashes with other installed python packages. You can do this with
```bash
$ python3 -m venv excalibur-env
$ source excalibur-env/bin/activate
```

You should now see the name of the environment in parenthesis your terminal prompt, for example:
```bash
(excalibur-env) tk-d193@ln03:/work/d193/d193/tk-d193>
```

You will have to activate the environment each time you login. To deactivate the environment run `deactivate`.

----

## Install the excalibur-tests framework
Now we can use `pip` to install the package in the virtual environment. Update pip to the latest version with 
```bash
pip install --upgrade pip
```
then install the framework with
```bash
$ pip install -e ./excalibur-tests
```
We used the `editable` flag `-e` because later in the tutorial you will edit the repository to develop a new benchmark. 

----

## Set configuration variables

Configure the framework by setting these environment variables

```bash
export RFM_CONFIG_FILES="$(pwd)/excalibur-tests/benchmarks/reframe_config.py"
export RFM_USE_LOGIN_SHELL="true"
```

----

## Install and configure spack

Finally, we need to install the `spack` package manager. The framework will use it to build the benchmarks. Clone spack with

```bash
$ git clone -c feature.manyFiles=true https://github.com/spack/spack.git
```

Then configure `spack` with

```bash
$ source ./spack/share/spack/setup-env.sh
```

Spack should now be in the default search path.

----

## Check installation was successful

You can check everything has been installed successfully by checking that `spack` and `reframe` are in path and the path to the ReFrame config file is set correctly

```bash
$ spack --version
0.19.0.dev0 (a8b1314d188149e696eb8e7ba3e4d0de548f1894)
$ reframe --version
4.3.0
$ ls $RFM_CONFIG_FILES
/work/d193/d193/tk-d193/excalibur-tests/benchmarks/reframe_config.py
```

---

## Environment summary

If you log out and back in, you will have to run some of the above commands again to recreate your environment. These are (from your `work` directory):

```
module load cray-python
source excalibur-env/bin/activate
export RFM_CONFIG_FILES="$(pwd)/excalibur-tests/benchmarks/reframe_config.py"
export RFM_USE_LOGIN_SHELL="true"
source ./spack/share/spack/setup-env.sh
```

----

# Run Sombrero Example

You can now use ReFrame to run benchmarks from the `benchmarks/examples` and `benchmarks/apps` directories. The basic syntax is 
```bash
reframe -c <path/to/benchmark> -r
```

----

## ARCHER2 specific commands

In addition, on ARCHER2, you have to provide the quality of service (QoS) type for your job to ReFrame on the command line with `-J`. Use the "short" QoS to run the sombrero example with
```bash
$ reframe -c excalibur-tests/benchmarks/examples/sombrero -r -J'--qos=short'
```
You may notice you actually ran four benchmarks with that single command! That is because the benchmark is parametrized. We will talk about it in the next section.

----

## Output sample

```bash!
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

## Benchmark output

You can find build and run logs in the `output/` directory of a successful benchmark. They record how the benchmark was built by spack and ran by ReFrame.

While the benchmark is running, the log files are kept in the `stage/` directory. They remain there if the benchmark fails to build or run.

You can find the performance log file from the benchmark in `perflogs/`. The perflog records the captured figures of merit, environment variables and metadata about the job.

---

# Postprocess Benchmark Results

Now let's look at the Benchmark performance results, and create a plot to visualise them.

----

## The perflog

After running the Sombrero benchmark once you should have a perflog in `perflogs/archer2/compute-node/SombreroBenchmark.log` that looks like this
```
job_completion_time|version|info|jobid|num_tasks|num_cpus_per_task|num_tasks_per_node|num_gpus_per_node|flops_value|flops_unit|flops_ref|flops_lower_thres|flops_upper_thres|spack_spec|display_name|system|partition|environ|extra_resources|env_vars|tags
2023-08-25T11:23:46|reframe 4.3.2|SombreroBenchmark %tasks=2 %cpus_per_task=2 /de04c10b @archer2:compute-node+default|4323431|2|2|1|null|1.31|Gflops/seconds|1.2|-0.2|None|sombrero@2021-08-16|SombreroBenchmark %tasks=2 %cpus_per_task=2|archer2|compute-node|default|{}|{"OMP_NUM_THREADS": "2"}|example
2023-08-25T11:23:48|reframe 4.3.2|SombreroBenchmark %tasks=1 %cpus_per_task=2 /c1c3a3f1 @archer2:compute-node+default|4323433|1|2|1|null|0.67|Gflops/seconds|1.2|-0.2|None|sombrero@2021-08-16|SombreroBenchmark %tasks=1 %cpus_per_task=2|archer2|compute-node|default|{}|{"OMP_NUM_THREADS": "2"}|example
2023-08-25T11:23:48|reframe 4.3.2|SombreroBenchmark %tasks=1 %cpus_per_task=1 /52e1ce98 @archer2:compute-node+default|4323434|1|1|1|null|0.67|Gflops/seconds|1.2|-0.2|None|sombrero@2021-08-16|SombreroBenchmark %tasks=1 %cpus_per_task=1|archer2|compute-node|default|{}|{"OMP_NUM_THREADS": "1"}|example
2023-08-25T11:23:48|reframe 4.3.2|SombreroBenchmark %tasks=2 %cpus_per_task=1 /c52a123d @archer2:compute-node+default|4323432|2|1|1|null|1.29|Gflops/seconds|1.2|-0.2|None|sombrero@2021-08-16|SombreroBenchmark %tasks=2 %cpus_per_task=1|archer2|compute-node|default|{}|{"OMP_NUM_THREADS": "1"}|example
```
Every time the same benchmark is run, a line is appended in this perflog. The perflog contains
- Some general info about the benchmark run, including system, spack, and environment info.
- The Figure(s) Of Merit (FOM) value, units, reference value, and lower and upper limits (`flops` in this case)
- The `display_name` field, which encodes the benchmark name and parameters (`SombreroBenchmark %tasks=... %cpus_per_task=...` in this case)
- Other quantities the user might want to compare performance for, passed as environment variables and encoded in the `env_vars` field.
- The benchmark `tag` - another way to encode benchmark inputs, defined by the benchmark developers.

----

## The plotting configuration file


There are tools to plot the FOMs of benchmarks against any of the other parameters in the perflog. This generic plotting is driven by a configuration YAML file. Let's make one, and save it in `excalibur-tests/post-processing/post_processing_config.yaml`.

The file needs to include
- Plot title 
- Axis information
- Data series
- Filters

----

## Title and Axes

Axes must have a value specified with a perflog column name or a benchmark parameter name, and units specified with either a perflog column name or a custom label (including `null`).
```yaml
title: Performance vs number of tasks and CPUs_per_task

x_axis:
  value: "tasks"
  units:
    custom: null

y_axis:
  value: "flops_value"
  units:
    column: "flops_unit"
```

----

## Data series

Display several plots in the same graph and group x-axis data by specified column values. Specify an empty list if the perflog only has one series. In our sombrero example, we have two parameters, Therefore we need to either filter down to one, or make them separate series. Let's use separate series:

Format: `[column_name, value]`
```yaml
series: [["cpus_per_task", "1"], ["cpus_per_task", "2"]]
```
**NOTE:** Currently, only one distinct `column_name` is supported. In the future, a second one will be allowed to be added. But in any case, unlimited number of series can be plotted for the same `column_name` but different `value`.

----


## Filtering

You can filter data rows based on specified conditions. Specify an empty list for no filters.

Format: `[column_name, operator, value]`, 
Accepted operators: "==", "!=", "<", ">", "<=", ">="
```yaml
filters: []
```

**NOTE:** I need to use the above filter because my perflog file is a bit dirty, after re-running the benchmarks a few times. Feel free to experiment with a dirtier perflog file (eg. the one in `excalibur-tests/post-processing` or a folder with several perflog files.

----

## Run the postprocessing

We can now run the postprocessing with
```bash
python post_processing.py <log_path> <config_path>
```
where
- `<log_path>` is the path to a perflog file or a directory containing perflog files.
- `<config_path>` is the path to the configuration YAML file.

In our case,
```bash
python excalibur-tests/post-processing/post_processing.py perflogs excalibur-tests/post-processing/post_processing_config.yaml
```

----

## View the Output

`scp` over the `Performance_vs_number_of_tasks_and_CPUs_per_task.html` file created in `excalibur-tests/post-processing`, and behold!

:::spoiler Image
![](https://hackmd.io/_uploads/rkgyyJaa3.png)
:::



---

# Create a Benchmark

In this section you will create a ReFrame benchmark by writing a python class that tells ReFrame how to build and run an application and collect data from its output. 

For simplicity, we use the [`STREAM`](https://www.cs.virginia.edu/stream/ref.html) benchmark. It is a simple memory bandwidth benchmark with minimal build dependencies.

----

## How ReFrame works

When ReFrame executes a test it runs a pipeline of the following stages

![](https://reframe-hpc.readthedocs.io/en/stable/_images/pipeline.svg)

You can customise the behaviour of each stage or add a hook before or after each of them.  For more details, read the [ReFrame pipeline documentation](https://reframe-hpc.readthedocs.io/en/stable/pipeline.html).

----

## Getting started

To get started, open an empty `.py` file where you will write the ReFrame class, e.g. `stream.py`. Save the file in a new directory e.g. `excalibur-tests/benchmarks/apps/stream`.

----

## Include ReFrame modules

The first thing you need is include a few modules from ReFrame. These should be available if the installation step was successful.

```python
import reframe as rfm
import reframe.utility.sanity as sn
```

----

## Create a Test Class

ReFrame has built-in support for the Spack package manager.
In the following we will use the custom class `SpackTest` we created for our `benchmarks` module, which provides a tighter integration with Spack and reduces the boilerplate code you'd otherwise have to include.

```python
from benchmarks.modules.utils import SpackTest

@rfm.simple_test
class StreamBenchmark(SpackTest):
```

The data members and methods detailed in the following sections should be placed inside this class.

----

## Add Build Recipe

We prefer installing packages via spack whenever possible. In this exercise, the spack package for `stream` already exists in the global spack repository.

The `SpackTest` base class takes care of setting up spack as the build system ReFrame uses. We only need to instruct ReFrame to install version `5.10` of the `stream` [spack package](https://spack.readthedocs.io/en/latest/package_list.html#stream) using the `openmp` variant.

```python
spack_spec = 'stream@5.10 +openmp'
```

Note that we did not specify a compiler. Spack will use a compiler from the spack environment. The complete spec is recorded in the build log.

----

## Add Run Configuration

The ReFrame class tells ReFrame where and how to run the benchmark. We want to run on one task on a full archer2 node using 128 OpenMP threads to use the full node.

```python
valid_systems = ['archer2']
valid_prog_environs = ['default']
executable = 'stream_c.exe'
num_tasks = 1
num_cpus_per_task = 128
time_limit = '5m'
```

----

## Add environment variables

Environment variables can be added to the `env_vars` attribute.

```python
env_vars['OMP_NUM_THREADS'] = f'{num_cpus_per_task}'
env_vars['OMP_PLACES'] = 'cores'
```

----

## Add Sanity Check

The rest of the benchmark follows the [Writing a Performance Test ReFrame Tutorial](https://reframe-hpc.readthedocs.io/en/latest/tutorial_basics.html#writing-a-performance-test). First we need a sanity check that ensures the benchmark ran successfully. A function decorated with the `@sanity_function` decorator is used by ReFrame to check that the test ran successfully. The sanity function can perform a number of checks, in this case we want to match a line of the expected standard output.

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

## Run Stream Benchmark

You can now run the benchmark in the same way as the previous sombrero example

```bash
reframe -c excalibur-tests/benchmarks/apps/stream/ -r --system archer2 -J'--qos=short'
```

----

## Sample Output
```bash=
reframe -c apps/stream/ -r --system archer2 -J'--qos=short'
[ReFrame Setup]
  version:           4.3.0
  command:           '/mnt/lustre/a2fs-work3/work/d193/d193/tk-d193/excalibur-env/bin/reframe -c apps/stream/ -r --system archer2 -J--qos=short'
  launched by:       tk-d193@ln04
  working directory: '/mnt/lustre/a2fs-work3/work/d193/d193/tk-d193/rsecon-demo'
  settings files:    '<builtin>', '/work/d193/d193/tk-d193/excalibur-tests/benchmarks/reframe_config.py'
  check search path: '/mnt/lustre/a2fs-work3/work/d193/d193/tk-d193/rsecon-demo/apps/stream'
  stage directory:   '/mnt/lustre/a2fs-work3/work/d193/d193/tk-d193/rsecon-demo/stage'
  output directory:  '/mnt/lustre/a2fs-work3/work/d193/d193/tk-d193/rsecon-demo/output'
  log files:         '/tmp/rfm-70arere5.log'

[==========] Running 1 check(s)
[==========] Started on Mon Jul 10 15:55:01 2023 

[----------] start processing checks
[ RUN      ] StreamBenchmark /8aeff853 @archer2:compute-node+default
[       OK ] (1/1) StreamBenchmark /8aeff853 @archer2:compute-node+default
P: Copy: 842018.4 MB/s (r:0, l:None, u:None)
P: Scale: 808540.5 MB/s (r:0, l:None, u:None)
P: Add: 959612.0 MB/s (r:0, l:None, u:None)
P: Triad: 941658.5 MB/s (r:0, l:None, u:None)
[----------] all spawned checks have finished

[  PASSED  ] Ran 1/1 test case(s) from 1 check(s) (0 failure(s), 0 skipped, 0 aborted)
[==========] Finished on Mon Jul 10 15:55:18 2023 
Log file(s) saved in '/tmp/rfm-70arere5.log'

```

----

## Interpreting STREAM results

With default compile options, STREAM uses arrays of 10 million elements. On a full ARCHER2 node, the default array size fits into cache, and the benchmark does not report the correct memory bandwidth. Therefore the numbers from this tutorial are not comparable with other, published, results.

To avoid caching, increase the array size during build by adding e.g. `stream_array_size=64000000` to the spack spec. 

----

## Parametrized tests

You can pass a list to the `parameter()` built-in function in the class body to create a parametrized test. You cannot access the individual parameter value within the class body, so any reference to them should be placed in the appropriate function, for example `__init__()`

Example: Parametrize the array size

```python
array_size = parameter(int(i) for i in [4e6,8e6,16e6,32e6,64e6])
def __init__(self):
    self.spack_spec = f"stream@5.10 +openmp stream_array_size={self.array_size}"
```

:::spoiler Array size parametrization output
```bash=
[----------] start processing checks
[ RUN      ] StreamBenchmark %array_size=64000000 /bbfd0e71 @archer2:compute-node+default
[ RUN      ] StreamBenchmark %array_size=32000000 /e16f9017 @archer2:compute-node+default
[ RUN      ] StreamBenchmark %array_size=16000000 /abc01230 @archer2:compute-node+default
[ RUN      ] StreamBenchmark %array_size=8000000 /51d83d77 @archer2:compute-node+default
[ RUN      ] StreamBenchmark %array_size=4000000 /8399bc0b @archer2:compute-node+default
[       OK ] (1/5) StreamBenchmark %array_size=16000000 /abc01230 @archer2:compute-node+default
P: Copy: 235935.4 MB/s (r:0, l:None, u:None)
P: Scale: 229579.2 MB/s (r:0, l:None, u:None)
P: Add: 164113.8 MB/s (r:0, l:None, u:None)
P: Triad: 160868.2 MB/s (r:0, l:None, u:None)
[       OK ] (2/5) StreamBenchmark %array_size=8000000 /51d83d77 @archer2:compute-node+default
P: Copy: 722571.9 MB/s (r:0, l:None, u:None)
P: Scale: 795364.3 MB/s (r:0, l:None, u:None)
P: Add: 845910.1 MB/s (r:0, l:None, u:None)
P: Triad: 857621.3 MB/s (r:0, l:None, u:None)
[       OK ] (3/5) StreamBenchmark %array_size=32000000 /e16f9017 @archer2:compute-node+default
P: Copy: 125276.1 MB/s (r:0, l:None, u:None)
P: Scale: 113126.7 MB/s (r:0, l:None, u:None)
P: Add: 100628.7 MB/s (r:0, l:None, u:None)
P: Triad: 104038.0 MB/s (r:0, l:None, u:None)
[       OK ] (4/5) StreamBenchmark %array_size=64000000 /bbfd0e71 @archer2:compute-node+default
P: Copy: 130526.3 MB/s (r:0, l:None, u:None)
P: Scale: 106487.7 MB/s (r:0, l:None, u:None)
P: Add: 104170.9 MB/s (r:0, l:None, u:None)
P: Triad: 106335.6 MB/s (r:0, l:None, u:None)
[       OK ] (5/5) StreamBenchmark %array_size=4000000 /8399bc0b @archer2:compute-node+default
P: Copy: 735439.6 MB/s (r:0, l:None, u:None)
P: Scale: 791845.0 MB/s (r:0, l:None, u:None)
P: Add: 951898.8 MB/s (r:0, l:None, u:None)
P: Triad: 949653.7 MB/s (r:0, l:None, u:None)
[----------] all spawned checks have finished

[  PASSED  ] Ran 5/5 test case(s) from 5 check(s) (0 failure(s), 0 skipped, 0 aborted)
[==========] Finished on Wed Aug 23 13:25:12 2023 

```
:::

----

## Reference values

ReFrame can automate checking that the results fall within an expected range. We can use it in our previous example of increasing the array size to avoid caching. You can set a different reference value for each `perf_key` in the performance function. For example, set the test to fail if it falls outside of +-25% of the values obtained with the largest array size.

```python
reference = {
    'archer2': {
        'Copy':  (130000, -0.25, 0.25, 'MB/s'),
        'Scale': (105000, -0.25, 0.25, 'MB/s'),
        'Add':   (105000, -0.25, 0.25, 'MB/s'),
        'Triad': (105000, -0.25, 0.25, 'MB/s')
    }
}
```

> The performance reference tuple consists of the reference value, the lower and upper thresholds expressed as fractional numbers relative to the reference value, and the unit of measurement. If any of the thresholds is not relevant, None may be used instead. Also, the units in this reference variable are entirely optional, since they were already provided through the @performance_function decorator.

----

## (extra) Tuning the performance

ReFrame allows you to [modify the parallel launcher command](https://reframe-hpc.readthedocs.io/en/stable/tutorial_advanced.html#modifying-the-parallel-launcher-command). Doing it too generally may break portability of benchmarks, and is not advised. However, we can target the `archer2` system specifically to get better performance on ARCHER2 by using

```python
@run_before('run')
def set_cpu_binding(self):
    if self.current_system.name == 'archer2':
        self.job.launcher.options = ['--distribution=block:block --hint=nomultithread']
```
Modify the reference values to match the improved performance.

Note: launcher options don't get recored in ReFrame logs

----

## Plotting STREAM benchmark output

:::spoiler Postprocessing config
```yaml
title: Stream Triad Bandwidth

x_axis:
  value: "array_size"
  units:
    custom: null

y_axis:
  value: "Triad_value"
  units: 
    column: "Triad_unit"

series: []
filters: [["test_name","==","StreamBenchmark"]]
```
:::

---

# Portability Demo

TODO: Move this to beginning

Having gone through the process of setting up the framework on multiple systems enables you to run benchmarks configured in the repository on those systems. As a proof of this concept, this demo shows how to run a benchmark (e.g. `hpgmg`) on a list of systems (ARCHER2, csd3, cosma8, isambard-macs). Note that to run this demo, you will need an account and a CPU time allocation on each of these systems.

----

The commands to set up and run the demo are recorded in [scripts in the exaclibur-tests repository](https://github.com/ukri-excalibur/excalibur-tests/tree/tk-portability-demo/demo). It is not feasible to make the progress completely system-agnostic, in our case we need to manually

- Load a compatible python module
- Specify the user account for charging CPU time
- Change the working directory and select quality of service (on ARCHER2)

That is done differently on each system. The framework attempts to automtically identify the system it is being run on, but due to ambiguity in login node names this can fail, and we also recommend specifying the system on the command line.

----

:::spoiler setup.sh
```bash
#!/bin/bash -l

system=$1

# System specific part of setup. Mostly load the correct python module
if [ $system == archer2 ]
then
    module load cray-python
    cd /work/d193/d193/tk-d193
elif [ $system == csd3 ]
then
    module load python/3.8
elif [ $system == cosma ]
then
    module swap python/3.10.7
elif [ $system == isambard ]
then
    module load python37
    export PATH=/home/ri-tkoskela/.local/bin:$PATH
fi

# Setup
mkdir demo
cd demo
python3 --version
python3 -m venv demo-env
source ./demo-env/bin/activate
git clone git@github.com:ukri-excalibur/excalibur-tests.git
git clone -c feature.manyFiles=true git@github.com:spack/spack.git
source ./spack/share/spack/setup-env.sh
export RFM_CONFIG_FILES="$(pwd)/excalibur-tests/benchmarks/reframe_config.py"
export RFM_USE_LOGIN_SHELL="true"
pip install --upgrade pip
pip install -e ./excalibur-tests
```
:::

----

:::spoiler run.sh
```bash
#!/bin/bash

app=$1
compiler=$2
system=$3
spec=$app\%$compiler

apps_dir=excalibur-tests/benchmarks/apps

if [ $system == archer2 ]
then
    reframe -c $apps_dir/$app -r -J'--qos=standard' --system archer2 -S spack_spec=$spec --setvar=num_cpus_per_task=8  --setvar=num_tasks_per_node=2 --setvar=num_tasks=8
elif [ $system == cosma ]
then
    reframe -c $apps_dir/$app -r -J'--account=do006' --system cosma8 -S spack_spec=$spec --setvar=num_cpus_per_task=8  --setvar=num_tasks_per_node=2 --setvar=num_tasks=8
elif [ $system == csd3 ]
then
    reframe -c $apps_dir/$app -r -J'--account=DIRAC-DO006-CPU' --system csd3-cascadelake -S spack_spec=$spec --setvar=num_cpus_per_task=8  --setvar=num_tasks_per_node=2 --setvar=num_tasks=8
elif [ $system == isambard ]
then
    reframe -c $apps_dir/$app -r --system isambard-macs:cascadelake -S build_locally=false -S spack_spec=$spec --setvar=num_cpus_per_task=8  --setvar=num_tasks_per_node=2 --setvar=num_tasks=8
fi
```
:::

---

# Useful Reading

----

## ReFrame

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

## Spack

- [Spack documentation](https://spack.readthedocs.io/)
- [Spack tutorial (including YouTube recordings)](https://spack-tutorial.readthedocs.io/)
- [Spack package searchable list](https://packages.spack.io/)

