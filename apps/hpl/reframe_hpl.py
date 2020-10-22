""" High Performance Linpack - Intel optimised version.

    Runs on a) a single node and b) all nodes.

    Run using e.g.:
        
        cd hpc-tests
        conda activate hpc-tests
        reframe/bin/reframe -C reframe_config.py -c apps/hpl/ --run --performance-report

    To run only "single" node or "all" node tests add the appropriate tag, e.g.:

        --tag single

    Requires files :
        - <repo_root>/systems/<sysname>/hpl/{single,all}/HPL.dat
    
    This uses the prebuilt binaries provided with MKL so the ReFrame partition/environment must include.

    The Intel HPL uses one MPI process per node and automatically generates TBB threads to use the available cores.
    Therefore PxQ in the HPL.dat should equal the number of nodes in the system.

    The following tags are defined:
    - Number of nodes to use: 'single' or 'all'
    - Total number of processes 'num_procs=<N>' and actual number of nodes 'num_nodes=<N>' where <N> is an integer
    - Git version: 'git=<describe>' where <describe> is output from git describe.
    Only the first is really useful to select tests, the others are provided for reporting purposes.

"""

import reframe as rfm
import reframe.utility.sanity as sn
import sys, os, shutil
sys.path.append('.')
import modules
from modules.reframe_extras import Scheduler_Info
from reframe.core.logging import getlogger

@rfm.parameterized_test(*[['single'], ['all']])
class IntelHpl(rfm.RunOnlyRegressionTest):
    """ See module docstring """
    
    def __init__(self, size):
        
        self.size = size
        self.valid_systems = ['*']
        self.valid_prog_environs = ['intel-hpl']
        self.sourcesdir = os.path.join(self.prefix, '..', '..', 'systems', self.current_system.name, 'hpl', size) # use self.prefix so relative to test dir, not pwd
        
        # NB num tasks etc done after setup
        self.exclusive_access = True
        self.time_limit = '1h'
        self.executable = '$MKLROOT/benchmarks/mp_linpack/xhpl_intel64_dynamic'
        
        git_ref = modules.utils.git_describe()
        self.tags |= {size, 'git=%s' % git_ref}

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

            # see hpl-2.3/testing/ptest/HPL_pdtest.c:{219,253-256} for pattern details - assuming Intel is the same
            'Gflops': sn.extractsingle(r'^W[R|C]\S+\s+\d+\s+\d+\s+\d+\s+\d+\s+\d[\d.]+\s+(\d[\d.eE+]+)', self.stdout, 1, float),
        }
        self.reference = {
            '*': {
                'Gflops': (None, None, None, 'Gflops'),
                }
        }

    
    @rfm.run_after('setup')
    def set_procs(self):
        rfm_part = self.current_partition
        self.num_tasks_per_node = 1
        self.num_nodes = {'single':1, 'all':Scheduler_Info(rfm_part).num_nodes}[self.size]
        self.num_tasks = self.num_nodes * self.num_tasks_per_node

        self.tags |= {'num_procs=%i' % self.num_tasks, 'num_nodes=%i' % self.num_nodes}
        