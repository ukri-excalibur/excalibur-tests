# Ramses

## Prerequisites

To run this test you will need to first download the necessary inputs

* `cosmo3d-IC-256.tar.gz`
* `cosmo3d-IC-322.tar.gz`
* `cosmo3d-IC-406.tar.gz`
* `cosmo3d-IC-512.tar.gz`

At present, they need to be downloaded manually from University of Edinburgh's [DataSync
service](https://datasync.ed.ac.uk/index.php/s/ju6knXo5TVchspd)

The password is `dirac3bm`

**Important** make sure that you move the downloaded data to the `ramses/data/` directory.

This workflow will be fully automated. We are just waiting to setup a centralized server where input data for tests can be
stored.

The class `Ramses_download_inputs` is setup to use `wget` as soon as the centralized server is ready. Just remove the two lines
below that manually overwrite the `wget` command.

```python
self.executable = 'cp'
self.executable_opts = [f'-r {input_dir} .']
```

## Usage

From the top-level directory of the repository, you can run the benchmarks with

```sh
reframe -c apps/ramses -r --performance-report
```

### Filtering the benchmarks

By default all benchmarks will be run. You can run individual benchmarks with the
[`--tag`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-0) option:

* `weak` to run the weak scaling benchmarks
* `strong` to run the weak scaling benchmarks

Examples:

```sh
reframe -c apps/ramses -r --performance-report --tag Weak
reframe -c apps/ramses -r --performance-report --tag Strong
```
