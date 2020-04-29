# hpc-tests
WIP tests for HPC systems using OpenHPC


# Setup

```shell
sudo yum install -y python-pip
sudo pip install -U pip # update pip
sudo pip install virtualenv
virtualenv .venv
. .venv/bin/activate
pip install -U -r requirements.txt # TODO:
```

If you need to set up a public Jupyter notebook server run:
```
cd setup
./jupyter-server.sh <<< PASSWORD # add a password here
cd ..
jupyter notebook
```