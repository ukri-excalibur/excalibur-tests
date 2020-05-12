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
import sys, os
sys.path.append('.')
from reframe_extras import CachedCompileOnlyTest   

@sn.sanity_function
def is_empty(path):
    """ Check `path` is an empty file """
    return not(os.path.getsize(path))


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
