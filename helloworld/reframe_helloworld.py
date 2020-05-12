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
import sys

@rfm.simple_test
class HelloworldTest(rfm.RegressionTest):
    def __init__(self):
        self.descr = 'Test of using reframe'
        self.valid_systems = ['sausage-newslurm:compute']
        self.valid_prog_environs = ['gnu8-openmpi3']
        self.sourcesdir = '.'
        self.sourcepath = 'helloworld.c'
        self.build_system = 'SingleSource'
        self.build_system.cc = 'mpicc'
        self.modules = []
        self.executable_opts = []
        self.sanity_patterns = sn.assert_found('newslurm.compute', self.stdout)
        self.perf_patterns = {}
        self.reference = {}
        self.num_tasks = 3
        self.num_tasks_per_node = 2
        self.keep_files = [self.executable]

if __name__ == '__main__':
    # hacky test of extraction:
    from reframe.utility.sanity import evaluate
    # with open(sys.argv[-1]) as f:
    #     stdout = f.read()
    # pprint(evaluate(imb_results(stdout, 'Uniband')))
