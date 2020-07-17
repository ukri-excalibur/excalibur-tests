# High Performance Linpack

Run HPL tests on one and all nodes.

# Installation using Spack

E.g.:

    spack load patch
    spack install hpl ^/ziwdzwh # openmpi dependency

# HPL .dat configuration files

Appropriate HPL configuration files named `HPL-single.dat` and `HPL-all.dat` for the single- and all-node cases respectively must be generated and placed in either:

- `<repo_root>/systems/<sysname>/hpl/`
- `<repo_root>/systems/<sysname>/<partition>/hpl/`

depending on whether system-wide or partition-specific configurations are required. ReFrame will copy these files into the staging directories before running a test, so changes made to these files will persist and apply to the next run.

As an example, the configuration files for AlaSKA were generated as follows:
- Run `sinfo -N --long` to get:
    - The number of nodes for the "all" case (16)
    - The number of physical cores per node (32) from the "S:C:T" field (S * C).
- Use Horizon to get memory per node (128GB)
- Run `srun --pty bash -i` to get a shell on a compute node and run `/proc/cpuinfo` to get processor type and therefore microarchitecture (E5-2683 v4, i.e. Broadwell).
- From [Intel documentation](https://software.intel.com/content/www/us/en/develop/documentation/mkl-linux-developer-guide/top/intel-math-kernel-library-benchmarks/intel-distribution-for-linpack-benchmark/configuring-parameters.html), get recommended block sizes for that processor  (192).
- Use [this](https://www.advancedclustering.com/act_kb/tune-hpl-dat-file/) tool with the above info to get initial configuration files.
- Place generated files in the above directories.

# Running tests

Run using e.g.:
        
    cd hpc-tests
    conda activate hpc-tests
    reframe/bin/reframe -C reframe_config.py -c hpl/ --run --performance-report

Only "single" node or "all" node tests can be run by adding the appropriate tag, e.g.:

    reframe/bin/reframe -C reframe_config.py -c hpl/ --run --performance-report --tag single

# Outputs

The ReFrame performance variables are:

- `Gflops`: The performance
- `git_ref`: The output from `git describe` on the `hpc-tests` repo.

This allows changes in performance to be linked to system configuration and HPL configuration (.dat file) changes.


# TODO:
- Try different PxQ - from [here](https://community.brightcomputing.com/question/how-do-i-run-the-hpl-test-on-a-bright-cluster-5d6614ba08e8e81e885f19f3):
    > Flat grids  like 4x1, 8x1, 4x2, etc. are good for ethernet-based networks.
- Will only handle a single test in the output at present