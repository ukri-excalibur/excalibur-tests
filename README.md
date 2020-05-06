# hpc-tests
WIP tests for OpenHPC systems using [reframe](https://reframe-hpc.readthedocs.io/en/latest/index.html) and [juypter](https://jupyter.readthedocs.io/en/latest/) notebooks.

Requires:
- OpenHPC + Slurm cluster with required modules (see individual test case READMEs)
- `git`, `wget`, `cmake` to be installed on the login node

# Setup

```shell
sudo yum install -y conda
conda create --name reframe python=3.7 pytest jsonschema jupyter matplotlib
conda init
```

It'll ask you to close and reopen your shell, so do that, then:
```shell
conda activate reframe
```

# TODO: sort .env file

If you need to set up a public Jupyter notebook server run):
```
cd setup
./jupyter-server.sh <<< PASSWORD # replace with a password for Jupyter
```
This only needs to be done once and sets up a self-signed SSL cert - note your browser will complain when connecting to the notebook.

To start jupyter, with the conda environment active run:
```shell
cd hpc-tests
jupyter notebook
```
