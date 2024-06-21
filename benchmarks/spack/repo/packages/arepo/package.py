import os

from spack.package import *

class Arepo(MakefilePackage):
    """Arepo is a massively parallel gravity and hydrodynamics code for astrophysical simulations."""
    homepage = "https://gitlab.mpcdf.mpg.de/vrs/arepo.git"
    git = "https://gitlab.mpcdf.mpg.de/vrs/arepo.git"
    
    
    version("master", branch="master")
   

    depends_on('mpi')
    depends_on('gsl')
    depends_on('hdf5')

    variant('fftw', default=False, description='FFTW support')
    variant('hdf5', default=True, description='HDF5 support')
    variant('hwloc', default=False, description='HWLOC support')
        
    depends_on('fftw',  when='+fftw')
    depends_on('hwloc', when='+hwloc')
    depends_on("mpich", when='^mpich')
    depends_on("openmpi", when='^openmpi')
    
    def edit(self, spec, prefix):
       
        copy('Template-Makefile.systype', 'Makefile.systype')
        copy('Template-Config.sh', 'Config.sh')
        
        specific_config_path = 'examples/yee_2d/Config.sh'
            
        self.config_file = specific_config_path  

        with open('Makefile.systype', 'w') as f:
            f.write('SYSTYPE="Darwin"\n')
    
        env["CC"] = spec["mpi"].mpicc
        env["CXX"] = spec["mpi"].mpicxx
        env["FC"] = spec["mpi"].mpifc
        env["F77"] = spec["mpi"].mpif77
    
    def build(self, spec, prefix):
        
        make('CONFIG={}'.format(self.config_file), 'BUILD_DIR=./build', 'EXEC=./Arepo')

    def install(self, spec, prefix):

        mkdirp(prefix.bin)
        install('./Arepo', prefix.bin)
        

    
        



  