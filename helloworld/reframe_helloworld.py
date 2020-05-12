""" Playground for seeing what reframe can do.

    Run using something like:
        
        conda activate reframe
        reframe/bin/reframe -c helloword/ --run

 TODO:

 - parameterise to different numbers of nodes/jobs-per-node

"""

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.utility.sanity import defer
from pprint import pprint
import sys, os, datetime, shutil
from reframe.core.logging import getlogger
from reframe.core.buildsystems import BuildSystem


class NoBuild(BuildSystem):
    def __init__(self):
        super().__init__()
    def emit_build_commands(self, environ):
        return []
    

@sn.sanity_function
def is_empty(path):
    """ Check `path` is an empty file """
    return not(os.path.getsize(path))

@rfm.simple_test
class Helloworld_Build(rfm.CompileOnlyRegressionTest):
    def __init__(self):

        self.descr = 'Build helloworld'
        self.valid_systems = ['sausage-newslurm:compute']
        self.valid_prog_environs = ['gnu8-openmpi3']
        self.modules = []
        self.sanity_patterns = is_empty(self.stdout)
        #self.keep_files = [self.executable]
    

    @rfm.run_before('compile')
    def conditional_compile(self):
        self.exes_dir = os.path.join('builds', self.current_system.name, self.current_partition.name, self.current_environ.name, self.name)
        exe = os.path.join(self.exes_dir, self.executable)
        if os.path.exists(exe):
            getlogger().info('found exe at %r', exe)
            self.build_system = NoBuild()
            src = os.path.join(self.stagedir, self.executable)
            dest = os.path.join(self.exes_dir, self.executable)
            shutil.copy(dest, src)
            #self.executable = exe
            #self.sourcesdir = None
            #self.sourcepath = ''
        else:
            self.sourcesdir = '.'
            self.sourcepath = 'helloworld.c'
            self.build_system = 'SingleSource'
            self.build_system.cc = 'mpicc'
        

    @rfm.run_after('compile')
    def copy_executable(self):
        self.exes_dir = os.path.join('builds', self.current_system.name, self.current_partition.name, self.current_environ.name, self.name)
        if not os.path.exists(self.exes_dir):
            os.makedirs(self.exes_dir)
        src = os.path.join(self.stagedir, self.executable)
        dest = os.path.join(self.exes_dir, self.executable)
        shutil.copy(src, dest)
        getlogger().info('copied exe to %r', dest)

def no_compile(self):
    getlogger().info('not compiling!')

@rfm.simple_test
class Helloworld_Run(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Run helloworld'
        self.valid_systems = ['sausage-newslurm:compute']
        self.valid_prog_environs = ['gnu8-openmpi3']
        self.sourcesdir = None
        self.modules = []
        self.executable_opts = []
        self.sanity_patterns = sn.assert_found('newslurm.compute', self.stdout)
        self.num_tasks = 3
        self.num_tasks_per_node = 2
        self.depends_on('Helloworld_Build')

    @rfm.require_deps
    def set_executable(self, Helloworld_Build):
        self.executable = os.path.join(Helloworld_Build().stagedir, Helloworld_Build().name)
        
if __name__ == '__main__':
    # hacky test of extraction:
    from reframe.utility.sanity import evaluate
    # with open(sys.argv[-1]) as f:
    #     stdout = f.read()
    # pprint(evaluate(imb_results(stdout, 'Uniband')))
