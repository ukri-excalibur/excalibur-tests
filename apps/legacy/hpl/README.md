# High Performance Linpack

Run Intel optimised HPL tests on one and all nodes.

This uses the pre-built binaries supplied with [Intel's MKL package](https://software.intel.com/content/www/us/en/develop/documentation/mkl-windows-developer-guide/top/intel-math-kernel-library-benchmarks/intel-distribution-for-linpack-benchmark/overview-of-the-intel-distribution-for-linpack-benchmark.html) - note Intel MPI is required.

# Installation of Intel-HPL using Spack

E.g.:

    spack load patch
    spack load gcc@9
    spack install intel-mpi %gcc@9:
    spack install intel-mkl %gcc@9:

This provides executables `$MKLROOT/benchmarks/mp_linpack/xhpl_intel64_{static,dynamic}`.

There are `runme_*` scripts in the same directory which may also provide useful hints to define the environment.


# HPL .dat configuration files

Appropriate `HPL.dat` configuration files must be generated and placed in `<repo_root>/systems/<sysname>/hpl/{single,all}` for single and all-node cases respectively. ReFrame will copy these files into the staging directories before running a test, so changes made to these files will persist and apply to the next run.

Hints:
- Generally, set PxQ to equal number of nodes, with P equal or smaller than Q (as using 1x MPI rank per node)
- Select problem size *N* to use e.g. 80% of total memory
- Check [Intel documentation](https://software.intel.com/content/www/us/en/develop/documentation/mkl-linux-developer-guide/top/intel-math-kernel-library-benchmarks/intel-distribution-for-linpack-benchmark/configuring-parameters.html) to select appropriate block size *NB*
- When running, check on a single node that `pstree` and `top` appear as expected.

# Running tests

Run using e.g.:
        
    cd hpc-tests
    conda activate hpc-tests
    reframe/bin/reframe -C reframe_config.py -c apps/hpl/ --run --performance-report

Only "single" node or "all" node tests can be run by adding the appropriate tag, e.g.:

    reframe/bin/reframe -C reframe_config.py -c hpl/ --run --performance-report --tag single

# Outputs

The ReFrame performance variables are:

- `Gflops`: The performance
- `git_ref`: The output from `git describe` on the `hpc-tests` repo.

This allows changes in performance to be linked to system configuration and HPL configuration (.dat file) changes.
