# HPCG benchmarks

These are based upon the [HPCG](https://hpcg-benchmark.org/) Conjugate Gradient solver benchmark.
At the time of writing, there are three benchmarks in the suite: the original implementation, one which solves the same problem with a hard-coded stencil, and one 
which solves a different problem with an [LFRic](https://www.metoffice.gov.uk/research/approach/modelling-systems/lfric) stencil and data.

## Usage

From the top-level directory of the repository, you can run the benchmarks with

```sh
reframe -c benchmarks/apps/hpcg -r --performance-report
```

You can use the `-n/--name` argument to pick `HPCG_Original / HPCG_Stencil / HPCG_LFRic` to select a particular benchmark.
Alternatively, if you want to compare the two implementations of the 27 point stencil problem (Original and Stencil), you can filter by tag `-t 27pt_stencil`.

This app is currently intended to be parallelized with MPI, and it is recommended to use the `--system` argument to pick up the appropriate hardware details, as well as Spack libraries.
