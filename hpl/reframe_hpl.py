""" High Performance Linpack.

    Run on all physical cores of a) 1 and b) all nodes

    Run using e.g.:
        
        cd hpc-tests
        conda activate hpc-tests
        reframe/bin/reframe -C reframe_config.py -c hpl/ --run --performance-report

    Requires files HPL-{single, all}.dat in one of:
        - <repo_root>/systems/<sysname>/hpl/
        - <repo_root>/systems/<sysname>/<partition>/hpl/
"""

import reframe as rfm
import reframe.utility.sanity as sn
import sys, os, shutil
sys.path.append('.')
import modules
from modules.reframe_extras import Scheduler_Info, CachedRunTest

@rfm.parameterized_test(*[['single'], ['all']])
class Hpl(rfm.RunOnlyRegressionTest, CachedRunTest):
    """ See module docstring """
    
    def __init__(self, size):
        
        self.valid_systems = ['*']
        self.valid_prog_environs = ['hpl']
        
        self.size = size
        num_nodes = {'single':1, 'all':Scheduler_Info().num_nodes}[size]        
        self.num_tasks_per_node = Scheduler_Info().pcores_per_node
        self.num_tasks = num_nodes * self.num_tasks_per_node
        self.exclusive_access = True
        self.executable = 'xhpl'
        self.time_limit = None
        
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

    @rfm.run_before('run')
    def copy_input(self):
        """ Copy the appropriate .dat file into staging.

            Can't just set sourcesdir as we only want one file.
        """
        dat_file = 'HPL-%s.dat' % self.size
        dat_source = None
        prefix = os.path.join(self.prefix, '..', 'systems', self.current_system.name) # use self.prefix so relative to test dir, not pwd
        suffixes = ['', self.current_partition.name]
        locations = [os.path.abspath(os.path.join(prefix, suffix, 'hpl', dat_file)) for suffix in suffixes]
        for location in locations:
            if os.path.exists(location):
                dat_source = location
        if dat_source is None:
            raise ValueError('.dat file not found in %s' % ' or '.join(locations))
        else:
            dat_dest = os.path.join(self.stagedir, 'HPL.dat')
            #raise NotImplementedError((dat_source, dat_dest))
            shutil.copy(dat_source, dat_dest)
            