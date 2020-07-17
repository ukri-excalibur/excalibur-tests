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
- From [this](https://ulhpc-tutorials.readthedocs.io/en/latest/parallel/mpi/HPL/#hpl-main-parameters) tutorial, a block size "NB" of 192 is suggested for Broadwell processors.
- Use [this](https://www.advancedclustering.com/act_kb/tune-hpl-dat-file/) tool with the above info to get initial configuration files.
- Place generated files in the above directories.


# TODO:
- Try different PxQ - from [here](https://community.brightcomputing.com/question/how-do-i-run-the-hpl-test-on-a-bright-cluster-5d6614ba08e8e81e885f19f3):
    > Flat grids  like 4x1, 8x1, 4x2, etc. are good for ethernet-based networks.
- Will only handle a single test in the output at present