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
reframe -c examples/sombrero -r --performance-report --system archer2 -J'--qos=serial'
reframe -c examples/sombrero -r --performance-report --system archer2 -J'--qos=short' -J'--account=t01'
```

Note that jobs run on specific queues, like `serial` and `lowpriority`, do not charge the corresponding project, but you need to have at least 1 [Computing Resource (CU)](https://docs.archer2.ac.uk/user-guide/scheduler/#cus) in budget to access them.

### Controlling CPU frequency

ARCHER2 allows [choosing the CPU frequency](https://docs.archer2.ac.uk/user-guide/energy/#controlling-cpu-frequency) during jobs by setting the environment variable `SLURM_CPU_FREQ_REQ` to specific values.
In ReFrame v3 the list of environment variables set by the framework is hold by the dictionary attribute called `variables`, and you can initialise it on the command line when running a benchmark with `-S`/`--setvar`.
The syntax to set dictionary items is a comma-separated list of `key:value` pairs: `-S dict=key_1:value_1,key_2:value_2`
For example, to submit a benchmark using the lowest CPU frequency (1.5 GHz) you can use

```
reframe -c examples/sombrero -r --performance-report --system archer2 -J'--qos=serial' -S variables=SLURM_CPU_FREQ_REQ:1500000
```

## CSD3

### Queue options

When submitting jobs to compute nodes, you need to specify the job queue, with the `--account` option to the scheduler.
To do this, when you run a benchmark you can use the `-J`/`--job-option` flag to `reframe` to specify the account, for example:

```
reframe -c examples/sombrero -r --performance-report --system csd3-skylake:compute-node -J'--accout=<ACCOUNT>'
```

where `<ACCOUNT>` is the project you want to charge.
You can see the account balance of your projects with the `mybalance` command.

## DIaL3

### Queue options

When submitting jobs to compute nodes, you need to specify the job queue, with the `--account` option to the scheduler.
To do this, when you run a benchmark you can use the `-J`/`--job-option` flag to `reframe` to specify the account, for example:

```
reframe -c examples/sombrero -r --performance-report --system csd3-skylake:compute-node -J'--accout=<ACCOUNT>'
```

where `<ACCOUNT>` is the project you want to charge.

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

## Tesseract

### Queue options

When submitting jobs to compute nodes, you need to specify the job queue, with the `--account` option to the scheduler.
To do this, when you run a benchmark you can use the `-J`/`--job-option` flag to `reframe` to specify the account, for example:

```
reframe -c examples/sombrero -r --performance-report --system tesseract:compute-node -J'--accout=<ACCOUNT>'
```

where `<ACCOUNT>` is the project you want to charge.

## Tursa

### Queue options

When submitting jobs to compute nodes, you need to specify the job queue, with the `--account` option to the scheduler.
To do this, when you run a benchmark you can use the `-J`/`--job-option` flag to `reframe` to specify the account, for example:

```
reframe -c examples/sombrero -r --performance-report --system tursa:compute-node -J'--accout=<ACCOUNT>'
```

where `<ACCOUNT>` is the project you want to charge.
