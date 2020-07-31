Gromacs Biomolecular Simulation:

http://manual.gromacs.org

Note Gromacs 2016 is required due to the benchmark file.

# Installation - OpenHPC

NB: Gromacs docs recommend fftw which is available as the OpenHPC package `fftw-gnu8-openmpi3-ohpc`; however docs recommend letting Gromacs install its own.

Assumes e.g.:
 - cmake
 - gnu8-compilers-ohpc
 - openmpi3-gnu8-ohpc


```
wget http://ftp.gromacs.org/pub/gromacs/gromacs-2016.4.tar.gz
tar -xf gromacs-2016.4.tar.gz
cd gromacs-2016.4
mkdir build_mpi
cd build_mpi
module load gnu8 openmpi3
cmake ../ -DGMX_MPI=ON -DGMX_OPENMP=ON -DGMX_GPU=OFF -DGMX_X11=OFF -DGMX_DOUBLE=OFF -DGMX_BUILD_OWN_FFTW=ON -DREGRESSIONTEST_DOWNLOAD=ON -DCMAKE_INSTALL_PREFIX=<wherever>
make
make check
make install # to DCMAKE_INSTALL_PREFIX above
```

# Installation - Spack

e.g.:

    spack install gromacs@2016.4 ^openmpi@4: fabrics=ucx schedulers=auto

Default variants should be appropriate.

See note in `imb/README.md` re. why openmpi4.

