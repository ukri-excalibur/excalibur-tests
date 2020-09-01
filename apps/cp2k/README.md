# CP2K

Performance tests of the CP2K quantum chemistry and solid state physics simluation package https://www.cp2k.org/ using the H20-256 benchmark distributed with the CP2K source code.

The benchmark is run on a range of number of nodes, from 1 up to all available. Each run uses as many processes per node as there are physical cores.

The following performance variables are captured:
- 'cp2k_time' (s): The "total maximum time" for the CP2K subroutine as reported in CP2K output. This is assumed to be processor time, not wallclock time.
- 'runtime_real' (s): Wallclock time reported by `time` for entire MPI program start to finish.

# Installation - Spack

This proved somewhat difficult due to spack issues. A working install required:

- Commenting out all `provides()` lines in the packages `intel-mkl`, `intel-parallel-studio`, and `cray-libsci` using `spack edit <package>`.
- Using `spack find -v <mpi-package>` to get the full description of the (openmpi) package, including variants. Unusually, using the hash ('/<hash>') did not work. This is being investigated by the spack maintainers.
- Running `spack install` for `cp2k` with this full specification, e.g.:

```shell
spack install cp2k%gcc@7.3.0 ^openmpi@4.0.3 ~atomics~cuda~cxx~cxx_exceptions+gpfs~java~legacylaunchers~memchecker~pmi+runpath~sqlite3+static~thread_multiple+vt fabrics=ucx schedulers=auto
```

Note that this is an MPI-only version - `cp2k+openmp` installs for MPI+OpenMP did not work (under investigation). Apart from this the spack variant defaults are appropriate.

# Usage

Run using e.g.:

    reframe/bin/reframe -C reframe_config.py -c apps/cp2k/ --run --performance-report

Run on a specific number of nodes by appending:

    --tag 'num_nodes=N$'

where N must be one of 1, 2, 4, ..., etc.