# hpc-tests
WIP tests for HPC systems using OpenHPC

Requires:
- OpenHPC + Slurm cluster with required modules (see individual test cases)
- `git`, `wget`, `cmake` to be installed on the login node
- `jq` to be installed on all nodes

# Setup

This is in the process of getting moved to conda because matplotlib wasn't installable with pip and didn't work with 
On the cluster login node run:

```shell
sudo yum install -y conda
conda create --name hpc-tests --python=2.7 # TODO: move to python3?
conda init
```

It'll ask you to close and reopen your shell, so do that, then:
```shell
conda activate hpc-tests
conda install numpy matplotlib jupyter
```

# TODO: sort .env file

# TODO: update this lot ...
```
virtualenv --system-site-packages .venv
. .venv/bin/activate
cd setup
pip install -U -r requirements.txt
```

If you need to set up a public Jupyter notebook server run:
```
cd setup
./jupyter-server.sh <<< PASSWORD # replace with a password for Jupyter
```

To start jupyter run:
```
cd hpc-tests
jupyter notebook
```

# Conventions

This uses a directory structure like:

Directory structure:
```
{repo}/{app}-{version}/
                       build.sh
                       setup.sh
                       run.sh
                       {system_name}-{compute_instance_type}/{compiler_family}-{mpi_family}/
```

Then in that last directory:
```
builds/
      {build_label}/
                  build.json
                  build/        # temporary files - transient
                  install/      # keep for duration
benchmarks/
      {bench_label}/
runs/
      {run_label/}
                  run.json
```

Each `{app}-{version}` directory should contain 3 scripts:

- `build.sh`: Downloads and compiles the application. Run:
      
      ./build.sh {system_name}-{compute_instance_type}/{compiler_family}-{mpi_family}/bin/build.json

- `setup.sh`: downloads and configures the benchmark
- `run.sh`: Run the benchmark

All of these are controlled by the `.json` files of the same name in the appropriate directory


TODO: Maybe the .json file should be common? But then how do we separate run and build options?
 - idea: have "build" key in `run.json` which points to/loads that file
TODO: results processing (started)