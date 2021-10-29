""" High Performance Conjugate Gradient - Intel-optimised version

    Run on all physical cores of a) a single and b) all nodes

    Run using e.g.:
        
        cd hpc-tests
        conda activate hpc-tests
        reframe/bin/reframe -C reframe_config.py -c hpcg/ --run --performance-report

    to run only "single" node or "all" node tests add the appropriate tag, e.g.:

        reframe/bin/reframe -C reframe_config.py -c hpcg/ --run --performance-report --tag single

    Requires files hpcg-{single, all}.dat in one of:
        - <repo_root>/systems/<sysname>/hpcg/
        - <repo_root>/systems/<sysname>/<partition>/hpcg/

    Follows recommendations for performance given in [Intel docs](https://software.intel.com/content/www/us/en/develop/documentation/mkl-linux-developer-guide/top/intel-math-kernel-library-benchmarks/intel-optimized-high-performance-conjugate-gradient-benchmark/choosing-best-configuration-and-problem-sizes.html)
"""

import reframe as rfm
import reframe.utility.sanity as sn
import sys, os, shutil
sys.path.append('.')
import modules
from modules.reframe_extras import Scheduler_Info, CachedRunTest
from reframe.core.logging import getlogger

@rfm.parameterized_test(*[['single'], ['all']])
class Hpcg(rfm.RunOnlyRegressionTest, CachedRunTest):
    """ See module docstring """
    
    def __init__(self, size):
        
        self.valid_systems = ['*']
        self.valid_prog_environs = ['intel-hpcg']

        self.size = size
        self.tags = set([size])
        num_nodes = {'single':1, 'all':Scheduler_Info().num_nodes}[size]        


        # from docs link above:
        # > run one MPI process per CPU socket and one OpenMP* thread per physical CPU core skipping SMT threads.
        self.num_tasks_per_node = Scheduler_Info().sockets_per_node
        threads_per_mpiproc = Scheduler_Info().pcores_per_node
        self.num_cpus_per_task = threads_per_mpiproc
        self.num_tasks = num_nodes * self.num_tasks_per_node
        self.variables = {
            'OMP_NUM_THREADS': str(threads_per_mpiproc)
        }
        self.exclusive_access = True
        self.executable = '$XHPCG_BIN'
        self.time_limit = None


        #self.git_ref = modules.utils.git_describe() # NB: load this during test instantiation, although we have to use a deferrable for perf variable
        
        self.use_cache = False # set to True to use cached results for debugging postprocessing of results

        #HPCG result is VALID with a GFLOP/s rating of 17.498100
        self.sanity_patterns = sn.assert_found('HPCG result is VALID', self.stdout)
        self.perf_patterns = {
            'Gflops': sn.extractsingle(r'.*\s([\d.Ee+]+)', self.stdout, 1, float),
        }
        self.reference = {
            '*': {
                'Gflops': (None, None, None, 'Gflop/s'),
                }
        }
    
    @rfm.run_before('run')
    def copy_file(self):
        """ Copy the appropriate .dat file into staging and the binary.

            Can't just set sourcesdir as we only want one file.
        """
        dat_file = 'hpcg-%s.dat' % self.size
        dat_source = None
        prefix = os.path.join(self.prefix, '..', 'systems', self.current_system.name) # use self.prefix so relative to test dir, not pwd
        suffixes = ['', self.current_partition.name]
        locations = [os.path.abspath(os.path.join(prefix, suffix, 'hpcg', dat_file)) for suffix in suffixes]
        for location in locations:
            if os.path.exists(location):
                dat_source = location
        if dat_source is None:
            raise ValueError('.dat file not found in %s' % ' or '.join(locations))
        else:
            dat_dest = os.path.join(self.stagedir, 'hpgc.dat')
            shutil.copy(dat_source, dat_dest)
            getlogger().info('copied %s to %s' % (dat_source, dat_dest))
