""" Playground for seeing what reframe can do.

    Run using something like:
        
        conda activate hpc-tests
        reframe/bin/reframe -c helloworld/ --run

 TODO:

 - parameterise to different numbers of nodes/jobs-per-node

"""

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.utility.sanity import defer
from pprint import pprint
import sys, os
sys.path.append('.')
import reframe_extras

@sn.sanity_function
def is_empty(path):
    """ Check `path` is an empty file """
    return not(os.path.getsize(path))


@rfm.simple_test
class Helloworld_Build(reframe_extras.CachedCompileOnlyTest):
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
    """ This runs one task per core, on as many nodes as are available """
    def __init__(self):
        self.descr = 'Run helloworld'
        self.valid_systems = ['*:compute']
        self.valid_prog_environs = ['*']
        self.sourcesdir = None
        self.modules = []
        self.executable_opts = []
        self.sanity_patterns = sn.assert_found('newslurm.compute', self.stdout)

        nodes = reframe_extras.slurm_node_info()
        n_cpus = sum(int(n['CPUS']) for n in nodes)

        self.num_tasks = n_cpus
        self.num_tasks_per_core = 1
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
