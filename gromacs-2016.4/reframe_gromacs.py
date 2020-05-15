''' Playground for seeing what reframe can do.

    Run using something like:
        
        conda activate reframe
        reframe/bin/reframe -c gromacs-2016.4/ --run # --performance-report

 TODO:
'''

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.utility.sanity import defer
from pprint import pprint
import sys, os, urllib, tarfile

sys.path.append('.')
from reframe_extras import CachedCompileOnlyTest

# TODO: note this is mpi/openmp version
# TODO: need to run make check (and possibly, make install, to avoid rebuilding again?)

@rfm.simple_test
class Gromacs_Build_Test(CachedCompileOnlyTest):

    @rfm.run_before('compile') # TODO: test this works ok with CachedCompileOnlyTest (in progress)
    def get_source(self):
        tar_name = 'gromacs-%s.tar.gz' % self.gromacs_version
        gromacs_url = 'http://ftp.gromacs.org/pub/gromacs/%s' % tar_name
        test_dir = os.path.dirname(__file__)
        tar_path = os.path.join(test_dir, 'downloads', tar_name)
        if not os.path.exists(os.path.dirname(tar_path)):
            os.mkdir(os.path.dirname(tar_path))
        if not os.path.exists(tar_path):
            urllib.request.urlretrieve(gromacs_url, tar_path)
        with tarfile.open(tar_path, 'r:gz') as tar:
            tar.extractall(os.path.join(test_dir, 'src'))
        untar_dir = os.listdir(os.path.join(test_dir, 'src'))[0]
        self.sourcesdir = os.path.join('src', untar_dir)
        

    def __init__(self):
        self.gromacs_version = '2016.4'
        self.descr = 'Test Gromacs'
        self.valid_systems = ['*:compute']
        self.valid_prog_environs = ['*']
        self.modules = []

        self.build_system = 'CMake'
        self.build_system.cc = 'mpicc'
        self.build_system.cxx = 'mpicxx'
        self.build_system.ftn = 'mpifort'
        self.build_system.config_opts = [
            '-DGMX_MPI=ON',
            '-DGMX_OPENMP=ON',
            '-DGMX_GPU=OFF',
            '-DGMX_X11=OFF',
            '-DGMX_DOUBLE=OFF',
            '-DGMX_BUILD_OWN_FFTW=ON',
            '-DREGRESSIONTEST_DOWNLOAD=ON',
        ]
        self.executable = os.path.join('bin', 'gmx_mpi')

        self.sanity_patterns = sn.assert_found('[100%] Built target mdrun_test_objlib', self.stdout)
        
        #self.reference = {}
        #self.num_tasks = 0
        #self.num_tasks_per_core = 1

if __name__ == '__main__':
    pass
    # hacky test of extraction:
    #from reframe.utility.sanity import evaluate
    # with open(sys.argv[-1]) as f:
    #     stdout = f.read()
    # pprint(evaluate(imb_results(stdout, 'Uniband')))
