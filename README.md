# hpc-tests

**NB This is a work-in-progress and READMEs etc may not be up to date**

Performance testing-as-code for HPC systems.

This package defines automated performance tests for HPC systems using both synthetic and MPI-based application benchmarks. It is designed to easily compare results from different systems, system configurations and/or environments (e.g. compilers & MPI libraries).

The intended test matrix is shown below, marked with (A) where there is an implementation (possibly not finalised) for the `AlaSKA` system:

| Application | Benchmark | MPI Library | Notes |
| ---         | ---       | ---         | --  |
| OSU Micro Benchmarks (OMB)       | latency (A), bandwidth (A), alltoall (A), allgather (A), allreduce (A)          | IntelMPI (A), OpenMPI (A)       | mbw_mr also added for AlaSKA for range of node numbers |
| Intel MPI Benchmarks (IMB)       | uniband (A), biband (A)                                                         | IntelMPI (A), OpenMPI (A)       | PingPong also added for AlaSKA for basic debugging |
| High Performance Linpack (HPL)   | -                                                                               | IntelMPI | Uses Intel-optimised version with MKL |
| High Performance Conjugate Gradient (HPCG) | -                                                                     | IntelMPI (A) | Uses Intel-optimised version with MKL |
| Castep                           | tbd                                                                             | tbd  | Requires licence  |
| CP2K                             | H20-256                                                                         | IntelMPI, OpenMPI (A)  |   |
| OpenFOAM                         | Motorbike                                                                       | IntelMPI, OpenMPI (A)  |   |
| GROMACS                          | HECBioSim benchmarks: 61k (A), 1.4M (A) and 3M atom cases (A)                   | IntelMPI, OpenMPI (A)  |   |
| WRF                              | CONUS 2.5km, CONUS 12.5kms, TBD                                                 | IntelMPI, OpenMPI  |   |
| TensorFlow                       | ResNet50                                                                        | tbd  |   |

For more information on the actual tests defined and how to run them see the README file in the relevant benchmark directory.

The [ReFrame](https://reframe-hpc.readthedocs.io/en/latest/index.html) framework is used to define tests in a portable fashion in the `reframe_<application>.py` file in each application directory.

Results are compared and plotted using [juypter notebooks](https://jupyter.readthedocs.io/en/latest/), with a `<application>.ipynb` file in each application directory.

This package does not automate build/install of the benchmarked applications themselves for your system. This allows it to be used to assess performance of current system application installs, custom builds, or for performance comparisons between different builds. However, for each benchmark installation instructions are provided using OpenHPC-provided packages (where relevant) and/or [Spack](https://spack.readthedocs.io/) (which does not require root).

## Repository Contents

Key repository contents are as follows:

```
apps/
    <application>/
        reframe_<application>.py    - the ReFrame tests for <application>
        <application>.ipynb         - jupyter notebook plotting results for <application>
modules/                            - python modules for functionality common to multiple tests
reframe/                            - the ReFrame installation
reframe_config.py                   - the description of each system for ReFrame
output/                             - ReFrame test output - see Reframe Concepts below
perflogs/                           - ReFrame performance logs - see Reframe Concepts below
```

## Installation

Ensure you have an HPC system with:
- `slurm` (while `ReFrame` itself can use other schedulers some extensions provided here are are currently slurm-specific)
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

1. Create and activate the `hpc-tests` conda environment:
    
        conda create -f environment.yml
        conda activate hpc-tests

1. Install ReFrame:

        cd hpc-tests
        git clone https://github.com/eth-cscs/reframe.git

1. Run ReFrame's own test suite:

        # ensure a compiler is available e.g. by loading a compiler module - NB: this is not shown in the ReFrame docs but is essential!
        cd reframe/
        ./test_reframe.py -v
  
    This will skip some tests but should not fail any.

1. Set up a public Jupyter notebook server:

        cd hpc-tests/setup
        ./jupyter-server.sh <<< PASSWORD
      
    Replacing `PASSWORD` with a password for Jupyter. This only needs to be done once and sets up a self-signed SSL certificate - note your browser will complain when connecting to the notebook.

1. If using `spack` to compile applications, install and set it up - see sections below.

1. For a new system, add it to the reframe configuration file `reframe_config.py` - see separate section below.


## ReFrame Concepts & Configuration

To configure these tests for a new system some understanding of ReFrame is necessary, so key aspects are defined here.

Tests in ReFrame are defined by Python scripts - here, the `apps/<application>/reframe_<application>.py` files. These define a generic test, independent of system details like scheduler, MPI libraries, launcher etc. These aspects are defined for the system(s) under test in the reframe configuration file `reframe_config.py`. A system definition contains one or more **partitions** which are not necessarily actual scheduler partitions, but simply logical separations within the system. Partitions then support one or more **environments** which describe the modules to be loaded, enviroment variables, options etc. Environments are defined separately from partitions so they may be specific to a system + partition, common to multiple systems or partitions, or a default environment may be overridden for specific systems and/or partitions. The third level is the **tests** themselves, which may also define modules to load etc. as well as which environments, partitions and systems they are valid for. ReFrame then runs tests on combinations of valid partitions + environments.

Despite this flexibility, in practice the features ReFrame exposes at each level affect how the system configuration should be defined. As an example, the setup for AlaSKA given in `reframe_config.py` covers:
  - Both HDR 100 InfiniBand and 25G Ethernet (RoCE) networks
  - Various MPI libraries and fabric libraries etc
  - Various compilers.

Note that:
- The environment variables used to select a network varies, depending on the MPI+fabric libraries. Therefore the compiler, MPI library + fabric variant and network selection environment variables must defined together in a **partition**.
- Because we use `spack` and/or `easybuild` to install packages, and the generated module names encode the compiler + MPI library chain, the application module names must be defined in the **environment**.
- The **tests** themselves can then be fully generic, without having to include logic for specific systems/partitions/environments.

## Adding a new system

Modify the following aspects of `reframe_config.py` - use the config for "alaska" as an example and follow ReFrame's [configuration documentation](https://reframe-hpc.readthedocs.io/en/stable/configure.html):
- Add a new system into the `"systems"` key.
- Add partitions to this system as required to cover your test matrix. Within each partition:
  - The "modules" defined here should be sufficent to load an MPI library (whether a compiler module must be specified to do that depends on how your module hierarchy is configured).
  - Define any environment variables required to get the scheduler and MPI library combination to function properly. The program and slurm sbatch scripts provided in `helloworld/` may be helpful in testing this.
- In the "environments" section, for each test you want to run on this system copy an existing test environment definition and change:
    - "target_systems" to list the "system:partition" combintations you want to run on
    - "modules" to specify the module(s) needed to run the appropriate benchmark within the specified partition.
  Note that depending on how benchmark modules are named, you may need to specify multiple environments with different partitions in "target_systems".

You also need to update various files in 'systems':
- `sysinfo.json` defines some properties for tested systems
- Other application/benchmark-specific files should be placed in a system-named directory - see the relevant README.

## Usage

All the below assumes the conda environment has been activated:

      conda activate hpc-tests

Firstly, run tests for one or more applications:

- If necessary, install the required application - see the appropriate `apps/<application>/README.md` for help.

- Run all tests for this application using something like:

      cd hpc-tests
      reframe/bin/reframe -C reframe_config.py -c <application>/ --run --performance-report

  Tests can be run for specfic systems/partitions by appending e.g.: `--system alaska:ib-gcc9-openmpi4-ucx`.
  Some tests also have tags which can be used to filter tests further - see the appropriate README.

- ReFrame will generate two types of output for each test:
    - Test outputs, including stdout, stderr and any results files which should be retained. These are copied to the `output/` directory tree, and overwritten each time a test is re-run.
    - "Performance variables", i.e. metrics extracted or computed from test outputs. These are defined in the tests themselves, and saved by ReFrame into a "performance log" in the `perflog/` directory tree. A performance log is a record-structured file with each line containing data for one performance variable from a run.

  Both of these use the same directory structure:

        <system>/<partition>/<environment>/test_directory/test/

Secondly, create/update plots for this system:

- Start the jupyter server:

      cd hpc-tests
      jupyter notebook

- Then browse to `https://<login-node-ip>:<port>` where port is given in the output from above, and login using the password you specified above.

- You will now see a file browser. Navigate to `apps/<application>/<application>.ipynb`.

- Step through the notebook using the play buttons.

- Once happy with results, commit to a branch.

# Spack

Spack setup is non-trivial and the docs/tutorials are somewhat out-of-date / missing info in places (details in [this bug](https://github.com/spack/spack/issues/16730)). This section will therefore try to describe how to get a working spack setup from scrach on an OpenHPC system using `tmod` for modules. However you should probably read the ["basic use"](https://spack.readthedocs.io/en/latest/basic_usage.html) section for concepts. The quick version is that spack installs packages as described by a "spec" which (as well as the version) can optionally describe the compiler and any dependencies (such as MPI libraries). Multiple specs of the same package may be installed at once.

## Setup

First, install:

    cd ~
    git clone https://github.com/spack/spack.git

Modify `~/.bashrc` to contain:

    export SPACK_ROOT=~/spack
    . $SPACK_ROOT/share/spack/setup-env.sh

This makes spack commands available in your shell, but **does not** integrate spack with your module system if that is `lmod` - contrary to what the documentation says.

Run:

    spack compiler list

and check a useful compiler is shown. If not, load the appropriate module, run:

    spack compiler find

and check it gets added.

Check if `patch` is available on your system. If not, install it using spack:

    spack install patch

Then load it - you will have to do this every time before running `spack install` (or add it to your .bashrc):

    spack load patch

At this point you could install other compilers using Spack if required - not shown here but essentially the same as the package install instructions below, plus the `spack compiler ...` commmands shown above.

Finally, as ReFrame cannot use `spack load` directly we need to enable spack's support for `lmod`:

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

- Rebuild any existing modules:

      spack module lmod refresh --delete-tree -y
  
  This only needs to be done once after modifying `modules.yaml`, all subsequent package installations will use these settings.

- Tell `lmod` where to find the module tree root, e.g.:

      module use $SPACK_ROOT/share/spack/lmod/linux-centos7-x86_64/Core/
  
- Add the `module use ...` command to your `~/.bashrc`.


## Installing Packages

Spack installs packages using a spec, for example to install openmpi integrated with the system slurm and using the ucx transport layer:

    spack install openmpi@4.0.3 fabrics=ucx schedulers=auto

Note that slurm integration - via pmix - appears to need openmpi v4 or greater. See [this PR](https://github.com/spack/spack/pull/10492) for details.)

Confirm the slurm integration using:

    spack load openmpi@4.0.3 # assuming this is the only spack-provided openmpi4 build
    ompi_info | grep slurm # should show various MCA components for slurm

For full details of spack spec formats see the documentation but in brief:

- The "@" suffix gives a version, and can be e.g. "@4" for latest v4, "@4:" for latest after v4 (e.g. possibly v5).
- The "a=b" portions are called "variants" - `spack list <package>` will show what defaults are.
- A compilier can optionally be specified too as e.g. "%gcc@9.0.3".

We can now install packages depending on this openmpi installation.

First, find the hash of the relevant openmpi installation, e.g. for the above:

    spack find -l openmpi@4.0.3

will return something like `ziwdzwh`.

Install a package using this MPI library, e.g.::

    spack spec -I gromacs@2016.4 ^openmpi/ziwdzwh

The `^` provides a spec for a dependency - normally this can just be another spack spec e.g. `openmpi@4:` but here we use `/<hash>` to ensure spack reuses the library we previously built, rather than building another openmpi package. This shouldn't generally be necessary but appears to be in this case due to some subtleties in how Spack handles dependencies with non-default options.

Note that before actually installing a package, you can use `spack spec -I` to process dependencies and see what is already installed, e.g.:

    spack spec -I gromacs@2016.4 %gcc@9: ^openmpi/qpsxmnc




# Adding a test

Some things which might help:
- `tools/report.py` is a CLI tool to interrogate performance logs.

Synthetic benchmarks will all be different, but application benchmarks should follow these conventions:
- Run under `time` and extract a performance variable 'runtime_real' (see e.g. `reframe_gromacs.py`).
- Run on 1, 2, 4, etc up to maximum number of nodes.
- Add tags 'num_procs=%i' and 'num_nodes=%i'.
