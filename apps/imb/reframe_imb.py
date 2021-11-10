""" Performance tests using Intel MPI Benchmarks.

    See README.md for details.

    For parallel-transfer tests (i.e. uniband and biband) which use multiple process pairs, the -npmin flag is passed so that only the specified number of processes is run on each test.
    This is the easiest way of ensuring proper process placement on the two nodes.

    Run using e.g.:

        reframe/bin/reframe -C reframe_config.py -c apps/imb/ --run --performance-report
"""

import reframe as rfm
import reframe.utility.sanity as sn
import sys, os, math
from collections import namedtuple
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from modules.imb import read_imb_out
from modules.reframe_extras import ScalingTest
from modules.utils import identify_build_environment

Metric = namedtuple('Metric', ['column', 'function', 'unit', 'label'])

class IMB_base(rfm.RegressionTest):
    METRICS = []

    def __init__(self):
        self.valid_systems = ['*:compute-node']
        self.valid_prog_environs = ['*']
        self.exclusive_access = True
        self.perf_patterns = {} # must do this
        self.perf_patterns = {} # something funny about reframe's attr lookup
        self.executable = 'IMB-MPI1'
        self.build_system = 'Spack'

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = ['intel-mpi-benchmarks@2019.6%intel']
        self.build_system.environment = identify_build_environment(self.current_system.name)

    @run_before('performance')
    def add_metrics(self):
        """ Create `self.perf_patterns` and units only in `self.reference`.

            Args:
                metrics: TODO
                n_procs: TODO

            TODO: Requires self.METRICS
        """

        for metric in self.METRICS:
            self.perf_patterns[metric.label] = reduce(self.stdout, self.num_tasks, metric.column, metric.function)
            self.reference[metric.label] = (0, None, None, metric.unit)

@sn.deferrable
def reduce(path, n_procs, column, function):
    """ Calculate an aggregate value from IMB output.

        Args:
            path: str, path to file
            n_procs: int, number of processes
            column: str, column name
            function: callable to apply to specified `column` of table for `n_procs` in `path`
    """
    tables = read_imb_out(path)
    table = tables[n_procs] # separate lines here for more useful KeyError if missing:
    col = table[column]
    result = function(col)
    return result

@rfm.simple_test
class IMB_PingPong(IMB_base):
    """ Runs on 2 nodes """
    METRICS = [
        # 'column' 'function', 'unit', 'label'
        Metric('Mbytes/sec', max, 'Mbytes/sec', 'max_bandwidth'),
        Metric('t[usec]', min, 't[usec]', 'min_latency'),
        Metric('t[usec]', max, 't[usec]', 'max_latency'),
    ]
    def __init__(self):
        super().__init__()
        self.executable_opts = ['pingpong']
        self.num_tasks = 2
        self.num_cpus_per_task = 1
        self.num_tasks_per_node = 1
        self.tags = {'pingpong'}

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found('# Benchmarking PingPong', self.stdout)

@rfm.simple_test
class IMB_MPI1(IMB_base):
    """
Runs both Uniband and Biband benchmarks on 2^1 ... 2^8 tasks. Uses the default strategy
which (hopefully) is to fill up nodes one by one. Should use 8 nodes at 256 tasks.
    """
    METRICS = [
        Metric('Mbytes/sec', max, 'Mbytes/sec', 'max_bandwidth')
    ]

    tasks = parameter([ 2 ** x for x in range(1,3)])
    
    # For possible modes see
    # https://www.intel.com/content/www/us/en/develop/documentation/imb-user-guide/top/mpi-1-benchmarks.html
    mode = parameter(['Uniband','Biband'])

    @run_after('setup')
    def set_options(self):
        self.executable_opts = [self.mode.lower(), '-npmin', str(self.num_tasks)]
        self.num_tasks = self.tasks
        self.num_cpus_per_task = 1
        self.tags = {self.mode.lower()}
        #TODO: What is the default behaviour if I don't set num_tasks_per_node?
        
    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found('# Benchmarking '+self.mode, self.stdout)
