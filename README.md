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
```
{repo}/{app}-{version}/{system_name}-{compute_instance_type}/{compiler_family}-{mpi_family}/bin/{BUILD_ID?}/
                                                                                 /run/{BUILD_ID?}/
```

Each `{app}-{version}` directory should contain 3 scripts:

- `build.sh`: downloads and compiles the application
- `setup.sh`: downloads and configures the benchmark
- `run.sh`: slurm sbatch script

All of these are controlled by `.json` files in the appropriate directory (e.g. `bin` for build step)

TODO: results processing.
TODO: build IDs and run IDs and integration
