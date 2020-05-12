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


class CachedCompileOnlyTest(rfm.CompileOnlyRegressionTest):
    """ TODO """
    @rfm.run_before('compile')
    def conditional_compile(self):
        build_dir = os.path.join('builds', self.current_system.name, self.current_partition.name, self.current_environ.name, self.name)
        build_path = os.path.join(build_dir, self.executable)
        if os.path.exists(build_path):
            self.build_path = build_path
            getlogger().info('found exe at %r', self.build_path)
            self.build_system = NoBuild()
            # have to copy it into the stage dir else we get:
            #  Failing phase: compile_wait
            #  OS error: [Errno 2] No such file or directory: '/mnt/nfs/hpc-tests/stage/sausage-newslurm/compute/gnu8-openmpi3/Helloworld_Build/./Helloworld_Build'
            dest = os.path.join(self.stagedir, self.executable)
            shutil.copy(self.build_path, dest)
            getlogger().info('copied to %r', dest)
            self.sourcesdir = None # have to set this to avoid the test dir getting copied over the stage dir         
        else:
            self.build_path = None

    @rfm.run_after('compile')
    def copy_executable(self):
        if not self.build_path: # i.e. actually did a compile:
            self.exes_dir = os.path.join('builds', self.current_system.name, self.current_partition.name, self.current_environ.name, self.name)
            if not os.path.exists(self.exes_dir):
                os.makedirs(self.exes_dir)
            exe_path = os.path.join(self.stagedir, self.executable)
            build_path = os.path.join(self.exes_dir, self.executable)
            shutil.copy(exe_path, build_path)
            getlogger().info('copied exe to %r', build_path)

@rfm.simple_test
class Helloworld_Build(CachedCompileOnlyTest):
    def __init__(self):

        self.descr = 'Build helloworld'
        self.valid_systems = ['sausage-newslurm:compute']
        self.valid_prog_environs = ['gnu8-openmpi3']
        self.modules = []
        self.sanity_patterns = is_empty(self.stdout)
        #self.keep_files = [self.executable]
        # set this stuff as normal for a build:
        self.sourcesdir = '.'
        self.sourcepath = 'helloworld.c'
        self.build_system = 'SingleSource'
        self.build_system.cc = 'mpicc'

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
        self.executable = os.path.join(Helloworld_Build().stagedir, Helloworld_Build().executable)
        
if __name__ == '__main__':
    # hacky test of extraction:
    from reframe.utility.sanity import evaluate
    # with open(sys.argv[-1]) as f:
    #     stdout = f.read()
    # pprint(evaluate(imb_results(stdout, 'Uniband')))
