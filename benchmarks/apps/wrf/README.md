# Weather Research and Forecasting (WRF) Model

Results from WRF, the [Weather Research & Forecasting Model](https://www.mmm.ucar.edu/weather-research-and-forecasting-model) using the [WRFV3 benchmarks](https://www2.mmm.ucar.edu/wrf/WG2/benchv3/):

- 12km CONUS (medium-size case), tag `12km`:
  > 48-hour, 12km resolution case over the Continental U.S. (CONUS) domain October 24, 2001 with a time step of 72 seconds. The benchmark period is hours 25-27 (3 hours), starting from a restart file from the end of hour 24.
- 2.5km CONUS (large case), tag `2.5km`:
  > Latter 3 hours of a 9-hour, 2.5km resolution case covering the Continental U.S. (CONUS) domain June 4, 2005 with a 15 second time step.  The benchmark period is hours 6-9 (3 hours), starting from a restart file from the end of the initial 6 hour period
Descriptions from the above benchmark page.

The following performance variables are captured:

- 'gflops': Gigaflops per second, calculated as described in the [benchmark page](https://www2.mmm.ucar.edu/wrf/WG2/benchv3/), using the average time required per model timestep and the number of floating point operations required for the benchmark. The time required for each model timestep is reported by WRF itself.


## Usage

Run using e.g.:

```
reframe/bin/reframe -C reframe_config.py -c apps/wrf/ --run --performance-report
```

A precursor task automatically downloads the required benchmark files.
This may take some time due to the files size.

### Filtering the benchmark

You can filter the benchmark to run by filtering by tag:

```sh
# For the 12km data
reframe/bin/reframe -c apps/wrf/ --run --performance-report --tag '12km'
# For the 2.5km data
reframe/bin/reframe -c apps/wrf/ --run --performance-report --tag '2.5km'
```

### Setting the number of threads and MPI processes

By default, these benchmarks will use

* [`num_cpus_per_task`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_cpus_per_task):
  2
* [`num_tasks`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_tasks):
  `current_partition.processor.num_cpus // min(1, current_partition.processor.num_cpus_per_core) // num_cpus_per_task`
* [`num_tasks_per_node`](https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.num_tasks_per_node): `current_partition.processor.num_cpus // num_cpus_per_task`

You can override the values of these variables from the command line with the
[`--setvar`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-S)
option, for example

```sh
reframe -c apps/wrf -r --performance-report --setvar=num_cpus_per_task=4 --setvar=num_tasks=16
```

_**Note**_: you're responsible for overriding these variables in a consistent
way, so that, for example, `num_tasks_per_node` doesn't exceed the number of
total tasks runnable on each node.
