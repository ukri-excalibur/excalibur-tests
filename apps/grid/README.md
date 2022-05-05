# GRID
ReFrame benchmark for the [GRID](https://github.com/paboyle/Grid) code.

### Compilation on csd3

```bash
mkdir $HOME/GRID && cd $HOME/GRID
git clone https://github.com/paboyle/Grid; cd Grid; git checkout release/dirac-ITT
module purge
module load intel/compilers/2020.4 intel/mkl/2020.4 intel/impi/2020.4/intel intel/libs/idb/2020.4 intel/libs/tbb/2020.4 intel/libs/ipp/2020.4 intel/libs/daal/2020.4 intel/bundles/complib/2020.4
```

Update eigen URL in the Makefile to point to 3.3.3 from https://gitlab.com/libeigen/eigen/-/releases

```bash
mkdir build; cd build
../configure --enable-simd=AVX512 --enable-comms=mpi3 --enable-mkl --prefix=$HOME/GRID CXX=mpicc
make -j 38
make check
make install
echo export PATH=$HOME/GRID/bin:$PATH >> ~/.bash_profile
source ~/.bash_profile
```
