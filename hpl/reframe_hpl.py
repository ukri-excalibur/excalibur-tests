""" High Performance Linpack.

    TODO: Describe where it runs.

    Run using e.g.:
        
        cd hpc-tests
        conda activate hpc-tests
        reframe/bin/reframe -C reframe_config.py -c hpl/ --run --performance-report

"""

import reframe as rfm
import reframe.utility.sanity as sn
import sys, os
sys.path.append('.')
import modules
from modules.reframe_extras import sequence, Scheduler_Info, CachedRunTest

node_seq = [2] # [Scheduler_Info().num_nodes]  TODO: make it run on all nodes

@rfm.parameterized_test(*[[n] for n in node_seq])
class Hpl(rfm.RunOnlyRegressionTest, CachedRunTest):
    """ Run on all physical cores of the specified number of nodes """
    
    def __init__(self, num_nodes):
        self.valid_systems = ['*']
        self.valid_prog_environs = ['hpl']
        
        self.executable = 'xhpl'
        self.num_tasks_per_node = Scheduler_Info().pcores_per_node
        self.num_tasks = num_nodes * self.num_tasks_per_node
        self.exclusive_access = True
        
        self.sourcesdir = os.path.join('..', 'systems', self.current_system.name, 'hpl') # TODO: optionally support partitions here?

        self.use_cache = False # set to True to use cached results for debugging postprocessing of results
        
        self.sanity_patterns = sn.assert_found('# TODO', self.stdout)
        