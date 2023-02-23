# TODO: Merge with #92 

## Archer 2

### Using python

ARCHER2 is a Cray system, and they [recommend using a cray optimised python version](https://docs.archer2.ac.uk/user-guide/python/). The HPE Cray Python distribution can be loaded using `module load cray-python`. This is necessary to pip install excalibur-tests following the instructions in [README.md](./README.md).

### Home partition

Spack has a limitation on the length of the path of the install tree. Because the path to the work directory on Archer2 is fairly long, we may exceed this limit when installing to the default directory used by pip. If you see an error in ReFrame beginning with

```
==> Error: SbangPathError: Install tree root is too long.
```
The work-around is to provide a shorter installation path to `pip`. Pass the installation path to `pip install` using `--target`, for example, `pip install --target = /work/<project_code>/<project_code>/<username>/pkg .`. Then add the `bin` subdirectory to `$PATH`, for example, `export PATH = /work/<project_code>/<project_code>/<username>/pkg/bin:$PATH`.
