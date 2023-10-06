# System-specific information

This framework strives to be as system-independent as possible, but there are some platform-specific details that you may need be aware of when running these benchmarks.
Below we collect some information you may want to keep in mind on the different systems.

## ARCHER2

### Home partition

ARCHER2 uses the standard Cray setup for which the home partition is ***not*** mounted on compute nodes, read [Data management and transfer](https://docs.archer2.ac.uk/user-guide/data/) for more details.
You likely want to install this benchmarking framework outside of your home directory, for example inside `/work/<project code>/<project code>/${USER}`, where `<project code>` is your project code.

### Queue options

When submitting jobs to compute nodes, you need to specify the job queue and maybe the project account.
The former is specified by setting the [Quality of Service](https://docs.archer2.ac.uk/user-guide/scheduler/#quality-of-service-qos), the latter is necessary if your user account is associated to multiple projects on ARCHER2 and you need to [specify which one to use](https://docs.archer2.ac.uk/user-guide/scheduler/#specifying-resources-in-job-scripts) for the submitted jobs.
We cannot automatically set these options for you because they are user-specific, but when you run a benchmark you can use the `-J`/`--job-option` flag to `reframe` to add new job options.
Some examples:

```
reframe -c benchmarks/examples/sombrero -r --performance-report --system archer2 -J'--qos=serial'
reframe -c benchmarks/examples/sombrero -r --performance-report --system archer2 -J'--qos=short' -J'--account=t01'
```

### Controlling CPU frequency

ARCHER2 allows [choosing the CPU frequency](https://docs.archer2.ac.uk/user-guide/energy/#controlling-cpu-frequency) during jobs by setting the environment variable `SLURM_CPU_FREQ_REQ` to specific values.
In ReFrame v3 the list of environment variables set by the framework is held by the dictionary attribute called `env_vars`, and you can initialise it on the command line when running a benchmark with `-S`/`--setvar`.
For more details, see Setting environment variables in [`README.md`](./README.md).
For example, to submit a benchmark using the lowest CPU frequency (1.5 GHz) you can use

```
reframe -c benchmarks/examples/sombrero -r --performance-report --system archer2 -J'--qos=serial' -S env_vars=SLURM_CPU_FREQ_REQ:1500000
```

### Using python

ARCHER2 is a Cray system, and they
[recommend using a cray optimised python version](https://docs.archer2.ac.uk/user-guide/python/).
The HPE Cray Python distribution can be loaded using `module load cray-python`.
This is necessary to pip install excalibur-tests following the instructions in [README.md](./README.md).

### Spack install path

Spack has a limitation of 127 characters on the length of the path of the install tree. Because the
path to the work directory on Archer2 is fairly long, and pip by default installs into
`<path/to/virtual/environment>/pythonx.x/site-packages/`we may exceed the limit when
installing to the default directory. If you see an error in ReFrame beginning with

```
==> Error: SbangPathError: Install tree root is too long.
```

A possible work-around is to provide a shorter installation path to `pip`. Pass the installation
path to `pip install` using `--target`, for example,
`pip install --target = /work/<project_code>/<project_code>/<username>/pkg .`.
Then add  the `bin` subdirectory to `$PATH`, for example,
`export PATH = /work/<project_code>/<project_code>/<username>/pkg/bin:$PATH`.

## CSD3

### Queue options

When submitting jobs to compute nodes, you need to specify the job queue, with the `--account` option to the scheduler.
To do this, when you run a benchmark you can use the `-J`/`--job-option` flag to `reframe` to specify the account, for example:

```
reframe -c benchmarks/examples/sombrero -r --performance-report --system csd3-skylake:compute-node -J'--accout=<ACCOUNT>'
```

where `<ACCOUNT>` is the project you want to charge.
You can see the account balance of your projects with the `mybalance` command.

## DIaL2

### Queue options

When submitting jobs to compute nodes, you need to specify the job queue, with the `--account` option to the scheduler.
To do this, when you run a benchmark you can use the `-J`/`--job-option` flag to `reframe` to specify the account, for example:

```
reframe -c benchmarks/examples/sombrero -r --performance-report --system dial2:compute-node -J'--accout=<ACCOUNT>'
```

where `<ACCOUNT>` is the project you want to charge.

Note: for exclusive access require to pass -J='-l naccesspolicy=SINGLEJOB -n'

## DIaL3

### Queue options

When submitting jobs to compute nodes, you need to specify the job queue, with the `--account` option to the scheduler.
To do this, when you run a benchmark you can use the `-J`/`--job-option` flag to `reframe` to specify the account, for example:

```
reframe -c benchmarks/examples/sombrero -r --performance-report --system dial3:compute-node -J'--accout=<ACCOUNT>'
```

where `<ACCOUNT>` is the project you want to charge.

## Isambard 2

### Multi-Architecture Comparison System (MACS) partition

#### Compilation on compute nodes

Login nodes on the Isambard 2 MACS partition have Intel "Broadwell" CPUs, but most of the compute nodes use CPUs of different microarchitecture, which means that you cannot directly compile optimised code for the compute nodes with Spack while on the login nodes.
To run compilation on the compute node, you have to set the attribute [`build_locally`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.build_locally) to `false` with `-S build_locally=false`, for example:

```
reframe -c benchmarks/examples/sombrero -r --performance-report --system isambard-macs:cascadelake -S build_locally=false
reframe -c benchmarks/examples/sombrero -r --performance-report --system isambard-macs:rome -S build_locally=false
```

You may also need to compile GPU applications on the compute nodes, as the login node does not have any GPUs (this really depends on the build system of the application at hand, whether it needs access to a GPU during the build or it is sufficient to have the GPU toolkit available).

### Phase3 partition

On the nodes with Nvidia Ampere GPUs, memory usage is restricted to 4 GiB by default.
To request more memory you [have to specify the resource](https://gw4-isambard.github.io/docs/user-guide/PHASE3.html#nvidia-gpu) `mem=...G`, for example by setting the `memory` key of `extra_resources` to the amount of memory you require.
This can be done on the command line of ReFrame with, for example

```
reframe ... -S extra_resources='{"memory": {"memory": "20G"}}'
```

to request a job with 20 GiB of memory.

## Myriad

### Python3 module

The only default Python in the system is currently Python 2.7, but this may change in the future.
Both ReFrame v3 and Spack v0.20 require Python v3.6 (at the moment most benchmarks should work also with Spack v0.18, but newer recipes may only be available in more recent versions of Spack), so you need to have a Python 3.6 available.
This is provided by the `python3` module in the system, the easiest thing to do is to add the lines

```sh
module load python3
export RFM_USE_LOGIN_SHELL="True"
```

to your shell init script (e.g. `~/.bashrc`).
The second line tells ReFrame to always load the shell init script when running the jobs, so that the Python3 module is available also during the jobs, to run Spack.

### Temporary directory for building packages with Spack

Before moving it to the final installation place, Spack builds software in a temporary directory.
By default on Myriad this is `/tmp`, but this directory is shared with other users and its partition is relatively small, so that building large software may always end up filling the entire disk, resulting in frequent `No space left on device` errors.
To work around this issue you can use as temporary directory the one pointed to by `XDG_RUNTIME_DIR`, which use a larger partition, reserved only to your user.
Note that this directory is automatically cleaned up after you log all of your sessions out of the system.
You can add the following line to your shell init script (e.g., `~/.bashrc`) to make `TMPDIR` use `XDG_RUNTIME_DIR`, unless otherwise set:

```sh
export TMPDIR="${TMPDIR:-${XDG_RUNTIME_DIR:-/tmp}}"
```

## Tursa

### Queue options

When submitting jobs to compute nodes, you need to specify the job queue, with the `--account` option to the scheduler.
To do this, when you run a benchmark you can use the `-J`/`--job-option` flag to `reframe` to specify the account, for example:

```
reframe -c benchmarks/examples/sombrero -r --performance-report --system tursa:compute-node -J'--accout=<ACCOUNT>'
```

where `<ACCOUNT>` is the project you want to charge.
