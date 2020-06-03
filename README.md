# hpc-tests

A work-in-progress HPC test system using:
- [reframe](https://reframe-hpc.readthedocs.io/en/latest/index.html) to run tests
- [juypter notebooks](https://jupyter.readthedocs.io/en/latest/) to show results

# Requirements

Essentially, an HPC system with slurm, modules and Python 3.

The intial proof-of-concept uses an OpenHPC-based system, but packages and their related modules could be provided by tools like `easybuild` or `spack` instead. Some builds are currently done by reframe itself (this may change) which requires `git`, `wget` and `cmake` to be installed on the login node.

While `reframe` itself copes  with other schedulers some extensions (in `reframe_extras/`) are currently slurm-specific.

Python 3 is required for jupyter notebooks.


# Setup

Clone this repo (assumed here into `hpc-tests`).

Install `conda`:

    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
    bash Miniconda3-latest-Linux-x86_64.sh
    # follow prompts to initialise
    # close/reopen shell

Create conda environment:
    
    conda create --name hpc-tests python=3.7 pytest jsonschema jupyter matplotlib
    conda activate hpc-tests

Install ReFrame:

    git clone https://github.com/eth-cscs/reframe.git

Check ReFrame works:

    # load a compiler, then
    cd reframe
    ./test_reframe.py -v

For a new system, add it to the reframe configuration file `reframe-settings.py`.

# TODO: sort .env file

If you need to set up a public Jupyter notebook server run:

    cd hpc-tests/setup
    ./jupyter-server.sh <<< PASSWORD # replace with a password for Jupyter

This only needs to be done once and sets up a self-signed SSL cert - note your browser will complain when connecting to the notebook.

# Usage

All the below assumes the conda enviroment is activated.

To run tests do something like:

    reframe/bin/reframe -C reframe-settings.py -c imb-2018.1/ --run --performance-report

To start jupyter, with the conda environment active run:

    cd hpc-tests
    jupyter notebook

Then browse to the given address using the password you specified above.


TODO:
- Add comments on using openhpc/spack
- add comment re `spack install/load patch`