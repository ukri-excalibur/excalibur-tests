

# Installation using Spack

E.g.
    spack load patch
    spack install hpl ^/ziwdzwh # openmpi dependency


# Generating an HPL configuration

As an example, here's how the one for AlaSKA was constructed:
- The OpenHPC cluster had 16 compute nodes.
- Use `srun --pty bash -i` to get to a compute node and run `/proc/cpuinfo` to get processor info: This shows E5-2683 v4 CPUs, i.e. Broadwell.
- Use `sinfo -N --long` to get other processor info, with the "S:C:T" field showing 32 physical cores per node.
- From [this](https://ulhpc-tutorials.readthedocs.io/en/latest/parallel/mpi/HPL/#hpl-main-parameters) tutorial, a block size "NB" of 192 is suggested for Broadwell processors.
- Use [this](https://www.advancedclustering.com/act_kb/tune-hpl-dat-file/) tool with the above info to get an initial file.
- Save this in `hpc-tests/systems/<system_name>/HPL.dat` - ReFrame will copy this to the test's staging dir before running a test


# TODO:
- Try different PxQ - from [here](https://community.brightcomputing.com/question/how-do-i-run-the-hpl-test-on-a-bright-cluster-5d6614ba08e8e81e885f19f3):
    > Flat grids  like 4x1, 8x1, 4x2, etc. are good for ethernet-based networks.
- Will only handle a single test in the output at present