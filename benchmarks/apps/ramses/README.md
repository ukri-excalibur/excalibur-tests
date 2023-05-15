# Ramses

## Prerequisites

This code is currently hosted on a private GitHub repo for the benchmarking purposes. If you want to run this benchmark you will
first need to request access. Please speak to the RSE team at Leicester for access.

This code requires the following input data.

* `cosmo3d-IC-256.tar.gz`
* `cosmo3d-IC-322.tar.gz`
* `cosmo3d-IC-406.tar.gz`
* `cosmo3d-IC-512.tar.gz`

They are publicly available on [zenodo](https://zenodo.org/record/7842140/).

*NB* They will be automatically downloaded by reframe, but it takes roughly 15 mins at 5MB/s. They will only be downloaded once
per run, but if you manually re-run tests you may prefer to use the following options
[`--restore-session`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-restore-session) and
[`--keep-stage-files`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-keep-stage-files).

## Usage

From the top-level directory of the repository, you can run the benchmarks with

```sh
reframe -c benchmarks/apps/ramses -r --performance-report
```

### Filtering the benchmarks

By default all benchmarks will be run. You can run individual benchmarks with the
[`--tag`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-0) option:

* `weak` to run the weak scaling benchmarks
* `strong` to run the strong scaling benchmarks

Examples:

```sh
reframe -c benchmarks/apps/ramses -r --performance-report --tag weak
reframe -c benchmarks/apps/ramses -r --performance-report --tag strong
```

## Compiler support

Currently, only the intel compiler is supported for this program.
