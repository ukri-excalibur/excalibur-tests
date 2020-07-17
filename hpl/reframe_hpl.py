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
from modules.reframe_extras import Scheduler_Info, CachedRunTest

@rfm.simple_test
class Hpl(rfm.RunOnlyRegressionTest, CachedRunTest):
    """ Run on all physical cores of the specified number of nodes """
    
    def __init__(self):
        self.valid_systems = ['*']
        self.valid_prog_environs = ['hpl']
        
        self.executable = 'xhpl'
        self.num_tasks_per_node = Scheduler_Info().pcores_per_node
        self.num_tasks = Scheduler_Info().num_nodes * self.num_tasks_per_node
        self.exclusive_access = True
        
        # this copies HPL.dat to staging dir:
        self.sourcesdir = os.path.join('..', 'systems', self.current_system.name, 'hpl') # TODO: optionally support partitions here?

        self.use_cache = False # set to True to use cached results for debugging postprocessing of results
        
        self.sanity_patterns = sn.all([
            sn.assert_found('End of Tests.', self.stdout),
            sn.assert_found('0 tests completed and failed residual checks', self.stdout),
            sn.assert_found('0 tests skipped because of illegal input values.', self.stdout)
        ])
        self.perf_patterns = {
            # e.g.:
            # T/V                N    NB     P     Q               Time                 Gflops
            # --------------------------------------------------------------------------------
            # WR11C2R4       46080   192    16    32              12.91             5.0523e+03

            # see hpl-2.3/testing/ptest/HPL_pdtest.c:{219,253-256} for pattern details
            'Gflops': sn.extractsingle(r'^W[R|C]\S+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d[\d.]+\s+(\d[\d.eE+]+)', self.stdout, 1, float)
        }
        self.reference = {
            '*': {'Gflops': (None, None, None, 'Gflops')}
        }

        