# hpc-tests

**NB This is a work-in-progress and READMEs etc may not be up to date**

Performance testing-as-code for HPC systems.

This package defines automated performance tests for HPC systems using both synthetic and MPI-based application benchmarks. It is designed to easily compare results from different systems, system configurations and/or environments (e.g. compilers & MPI libraries).

The current sythetic benchmarks are:
- Selected tests from Intel MPI Benchmarks (`imb/`)
- Selected OSU Micro Benchmarks (`omb/`)
- High Performance Linkpack (`hpl/`)

The current application benchmarks are:
- Gromacs: 3x HECBioSim benchmarks of varying sizes (`gromacs/`)

For more information on the actual tests defined and how to run them see the README file in the relevant benchmark directory.

The [ReFrame](https://reframe-hpc.readthedocs.io/en/latest/index.html) framework is used to define tests in a portable fashion in the `reframe_*.py` in each benchmark directory.

Results are compared and plotted using [juypter notebooks](https://jupyter.readthedocs.io/en/latest/), with a `<benchmark>.ipynb` file in each benchmark directory.

This package does not automate build/install of the benchmark packages for your system. This allows it to be used to assess performance of current system packages, custom builds, or for performance comparisons between different builds. However, for each benchmark installation instructions are provided using OpenHPC-provided packages (where relevant) and/or [Spack](https://spack.readthedocs.io/) (which does not require root).

## Repository Contents

Key repository contents are as follows:

```
<application>/
  reframe_<application>.py      - the ReFrame tests for <application>
  <application>.ipynb           - jupyter notebook plotting results for <application>
modules/                        - python modules for functionality common to multiple tests
reframe/                        - the ReFrame installation
reframe_config.py               - the description of each system for ReFrame
output/                         - ReFrame test output - see above
perflogs/                       - ReFrame performance logs - see above
```

## Installation

Ensure you have an HPC system with:
- `slurm` (`reframe` itself can use other schedulers some extensions provided here are are currently slurm-specific)
- a module system
- `git`

Python 3.6+ and various python modules will be required (due to ReFrame) - instructions here use [conda](https://docs.anaconda.com/anaconda/) to provide this.
Some way of compiling applications is required  - instructions here use `spack` which has its own [prerequisites](https://spack.readthedocs.io/en/latest/getting_started.html#prerequisites).


1. Clone this repo:

        git clone git@github.com:stackhpc/hpc-tests.git

1. Install `conda`:
  
        wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
        bash Miniconda3-latest-Linux-x86_64.sh
      
   Follow prompts to initialise, then close/reopen shell.

1. Create conda environment:
    
        conda create --name hpc-tests python=3.7 pytest jsonschema jupyter matplotlib pandas
        conda activate hpc-tests

    TODO: sort .env file

1. Install ReFrame:

        cd hpc-tests
        git clone https://github.com/eth-cscs/reframe.git

1. Run ReFrame's own test suite:

        # load a compiler module - NB: not shown in ReFrame docs but essential!
        cd reframe/
        ./test_reframe.py -v
  
    (This will skip some tests but should not fail any.)

1. Set up a public Jupyter notebook server:

        cd hpc-tests/setup
        ./jupyter-server.sh <<< <PASSWORD>
      
    Replacing `<PASSWORD>` with a password for Jupyter. This only needs to be done once and sets up a self-signed SSL certificate - NB your browser will complain when connecting to the notebook.

1. If using `spack` to compile applications, install and set it up - see separate section below.


1. For a new system, add it to the reframe configuration file `reframe_config.py` - see separate section below.


## ReFrame Concepts & Configuration

To configure these tests for a new system some understanding of ReFrame is necessary, so key aspects are defined here.

Tests in ReFrame are defined by Python scripts - here, the `<benchmark>/reframe_<benchmark>.py` files. These define a generic test, independent of system details like scheduler, MPI libraries, launcher etc. These aspects are defined for the system(s) under test in the reframe configuration file `reframe_config.py`. A system definition contains one or more **partitions** which are not necessarily actual scheduler partitions, but simply logical separations within the system. Partitions then support one or more **environments** which describe the modules to be loaded, enviroment variables, options etc. Environments are defined separately from partitions so they may be specific to a system + partition, common to multiple systems or partitions, or a default environment may be overridden for specific systems and/or partitions. Tests themselves may also define modules to load etc. as well as which environments, partitions and systems they are valid for. ReFrame then runs tests on combinations of valid partitions + environments.

Despite this flexibility, in practice the features ReFrame exposes at each level affect how the system configuration should be defined. Using the setup for AlaSKA given in `reframe_config.py` as an example:
- We want to run tests using both the HDR 100 InfiniBand and 25G Ethernet (RoCE) networks, and with OpenMPI using both 'openib' and 'ucx' to select between networks which requires two different builds of OpenMPI (which happen to be different versions here as well). This also needs to be expandable to multiple compiler + MPI library chains.
- Because of the two OpenMPI builds, the actual modules required for the benchmark applications have different names in each partition - this is likely to generally be the case without special attention to the module tree. Therefore the benchmark module cannot be defined at test level.
- We therefore define partitions which encapsulate *combinations* of the network (`ib-` or `roce-`), MPI library (`-openmpi3-` or `-openmpi4-`) and communication layer (`-openib` or `-ucx`). The partition also defines the scheduler to use (`slurm`), launcher (`srun`) and process management library (`pmix_v2`) and associated options. If using multiple compilers, the compiler definition would have to be incorporated into the partition name too.
- We then define an environment name per application, e.g. `imb`, and mark each test as valid only for that environment. We then provide separate *definitions* of these environments as required for individual partitions.

ReFrame captures two outputs from tests:
- Test outputs, including stdout, stderr and any results files which should be retained. These are copied to the `output/` directory tree, and overwritten each time a test is re-run.
- "Performance variables", i.e. metrics extracted or computed from test outputs. These are defined in the tests themselves, and saved by ReFrame into a "performance log" in the `perflog/` directory tree. A performance log is a record-structured file with each line containing data for one performance variable from a run.

Both of these use the same directory structure:

    <system>/<partition>/<environment>/test_directory/test/

## Adding a new system
Assuming you have read the above section on ReFrame concepts, you will have to modify the following aspects of `reframe_config.py`, using the config for "alaska" as an example:
- Add a new system into the `"systems"` key.
- Add partitions to this system as required to cover your test matrix.
- Within each partition:
  - The "modules" defined here should be sufficent to load an MPI library (whether a compiler module must be specified to do that depends on how your module hierarchy is configured).
  - Define any environment variables required to get the scheduler and MPI library combination to function properly. The program and slurm sbatch scripts provided in `helloworld/` may be helpful in testing this.
- In the "environments" section, for each test you want to run on this system copy an existing test environment definition and change:
    - "target_systems" to list the "system:partition" combintations you want to run on
    - "modules" to specify the module(s) needed to run the appropriate benchmark within the specified partition.
  Note that depending on how benchmark modules are named, you may need to specify multiple environments with different partitions in "target_systems".

# Usage

- All the below assumes the conda enviroment is activated:

      conda activate hpc-tests

- Install the required application/benchmark - see the appropriate README for help.

- Run tests using something like:

      cd hpc-tests
      reframe/bin/reframe -C reframe_config.py -c <application>/ --run --performance-report

  See appropriate README for application-specific instructions.

- To start jupyter, with the conda environment active run:

      cd hpc-tests
      jupyter notebook

  Then browse to the given address using the password you specified above.

# Spack

Spack setup is non-trivial and the docs/tutorials are somewhat out-of-date / missing info in places (details in [this bug](https://github.com/spack/spack/issues/16730)). This section will therefore try to describe how to get a working spack setup from scrach on an OpenHPC system using `tmod` for modules. However you should probably read the ["basic use"](https://spack.readthedocs.io/en/latest/basic_usage.html) section for concepts. The quick version is that spack installs packages as described by a "spec" which (as well as the version) can optionally describe the compiler and any dependencies (such as MPI libraries). Multiple specs of the same package may be installed at once.

First, install:

    cd ~
    git clone https://github.com/spack/spack.git

Modify `~/.bashrc` to contain:

    export SPACK_ROOT=~/spack
    . $SPACK_ROOT/share/spack/setup-env.sh

This makes spack commands available in your shell, but **does not** integrate spack with your module system if that is `lmod` - contrary to what the documentation says.

Run:

    spack compiler list

and check a useful compiler is shown. If not, load the appropriate module, run

    spack compiler find

and check it gets added.

Check if `patch` is available on your system. If not, install it using spack:

    spack install patch

Then load it - you will have to do this every time before running `spack install` (or add it to your .bashrc):

    spack load patch

If you want to use a non-default compiler also load that either via spack (e.g. `spack load gcc@7.0.4`) or your module system.

(At this point you could install other compilers using Spack if required - not shown here but essentially the same as MPI library instructions below + `spack compiler ...` commmands shown above.)

We can now install MPI libraries, for example for openmpi use:

    spack install openmpi@4.0.3 fabrics=ucx schedulers=auto

This should integrate with the system slurm - confirm this using:

    spack load openmpi@4.0.3 # assuming this is the only spack-provided openmpi4 build
    ompi_info | grep slurm # should show various MCA components for slurm

Note this integration (via pmix) appears to need openmpi v4 or greater - see this [PR etc.](https://github.com/spack/spack/pull/10492) for details.

Now find the hash of this openmpi installation:

    spack find -l openmpi@4:

Make a note of the hash shown, e.g. `ziwdzwh`.

Next we install a package using this MPI library, e.g.::

    spack install gromacs@2016.4 ^/ziwdzwh

The `^` tells spack another spec follows for a dependency of the package - normally this can just be another spack spec e.g. `openmpi@4:` but here we use `/<hash>` ensure spack reuses the library we previously built, rather than building another openmpi package. This shouldn't be necessary but appears to be some issue with spack's dependency handling.

Finally as ReFrame cannot use `spack load` directly we need to enable spack's support for `lmod`:

- Firstly, modify `~/.spack/modules.yaml` to e.g.:

      modules:
        enable::
          - lmod
        <snip>
        lmod:
          core_compilers:
            - gcc@7.3.0
          hierarchy:
            - mpi

  This:
    - Tells spack to use `lmod` as the module system (the "::" means only use this)
    - Lists the compiler(s) to use as the entry point to the module tree.
    - Tells spack to base the tree on the mpi library dependency for packages.

- Rebuild the modules:

      spack module lmod refresh --delete-tree -y
  
  This only needs to be done once after modifying `modules.yaml`, all subsequent package installations will use these settings.

- Tell `lmod` where to find the module tree root, e.g.:

      module use $SPACK_ROOT/share/spack/lmod/linux-centos7-x86_64/Core/
  
  Check this is correct using:
  
      module avail  # should show your spack-installed mpi
      module load <mpi_library>
      module avail  # should now show spack-installed applications depending on that mpi

- Add the `module use ...` command this to your `~/.bashrc`.


# TODO:

- update application readmes to reference these spack hints
