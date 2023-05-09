# Trove Pdsyev

## Prerequisites

This code is currently hosted on a private GitHub repo for the benchmarking purposes. If you want to run this benchmark you will
first need to request access. Please speak to the RSE team at Leicester for access.

The main code is publicly available at [https://github.com/Trovemaster/PDSYEV](https://github.com/Trovemaster/PDSYEV) but the
spack recipe is not currently set up to work with it. We are working on this and soon we will switch over to the public version.
This is because we need to be able to verify that the version we run is the same as the one already used for benchmarking.

## Usage

From the top-level directory of the repository, you can run the benchmarks with

```sh
reframe -c benchmarks/apps/trove-pdsyev -r --performance-report
```

### Filtering the benchmarks

By default all benchmarks will be run. You can run individual benchmarks with the
[`--tag`](https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-0) option:

* `single-node` to run benchmarks on a single node

Examples:

```sh
reframe -c benchmarks/apps/trove-pdsyev -r --performance-report --tag single-node
```
