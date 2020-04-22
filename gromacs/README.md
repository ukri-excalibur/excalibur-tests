Gromacs (Biomolecular Simulation):

http://manual.gromacs.org

assumes e.g.:
 - cmake
 - gnu8-compilers-ohpc
 - openmpi3-gnu8-ohpc

install of 2016.4:

NB: Gromacs docs recommend fftw which is available as `fftw-gnu8-openmpi3-ohpc`; however docs recommend letting Gromacs install it's own.

```
wget http://ftp.gromacs.org/pub/gromacs/gromacs-2016.4.tar.gz
tar -xf gromacs-2016.4.tar.gz
cd gromacs-2016.4
mkdir build_mpi
cd build_mpi
module load gnu8 openmpi3
cmake ../ -DGMX_MPI=ON -DGMX_OPENMP=ON -DGMX_GPU=OFF -DGMX_X11=OFF -DGMX_DOUBLE=OFF -DGMX_BUILD_OWN_FFTW=ON -DCMAKE_INSTALL_PREFIX=<wherever>
make
make check
make install # to DCMAKE_INSTALL_PREFIX above
```


