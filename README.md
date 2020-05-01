# hpc-tests
WIP tests for HPC systems using OpenHPC

Requires:
- OpenHPC + Slurm cluster with required modules (see individual test cases)
- `git`, `wget`, `cmake` to be installed on the login node
- `jq` to be installed on all nodes

# Setup

On the cluster login node run:

```shell
sudo yum install -y python-pip
sudo pip install -U pip # update pip
sudo pip install virtualenv
virtualenv .venv
. .venv/bin/activate
pip install -U -r requirements.txt
```

If you need to set up a public Jupyter notebook server run:
```
cd setup
./jupyter-server.sh <<< PASSWORD # replace with a password for Jupyter
cd ..
jupyter notebook
```

# Conventions

This uses a directory structure like:

TODO: don't actually use {build_id} or {version} at the moment

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
TODO: results processing.
TODO: build IDs and run IDs and integration
