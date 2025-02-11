=== "Cosma"

    This tutorial is run on the [Cosma](https://cosma.readthedocs.io/en/latest/) supercomputer.
    It should be straightforward to run on a different platform, the requirements are  `gcc 4.5`, `git 2.39` and `python 3.7` or later. 
	(for the later parts you also need `make`, `autotools`, `cmake` and `spack` but these can be installed locally).
    Before proceeding to install ReFrame, we recommend creating a python virtual environment to avoid clashes with other installed python packages.
    First load a newer python module.
    ```bash
    module swap python/3.10.12
    ```

=== "ARCHER2"

    This tutorial is run on ARCHER2, you should have signed up for a training account before starting.
    It can be ran on other HPC systems with a batch scheduler but will require making some changes to the config.
    Before proceeding to install ReFrame, we recommend creating a python virtual environment to avoid clashes with other installed python packages.
    First load the system python module.
    ```bash
    module load cray-python
    ```

Then create an environment and activate it with

```bash
python3 -m venv reframe_tutorial
source reframe_tutorial/bin/activate
```

You will have to activate the environment each time you login. To deactivate the environment run `deactivate`.
