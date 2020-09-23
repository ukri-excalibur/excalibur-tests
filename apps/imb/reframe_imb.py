""" Performance tests using Intel MPI Benchmarks.

    See README.md for details.

    For parallel-transfer tests (i.e. uniband and biband) which use multiple process pairs, the -npmin flag is passed so that only the specified number of processes is run on each test.
    This is the easiest way of ensuring proper process placement on the two nodes.

    Run using e.g.:

        reframe/bin/reframe -C reframe_config.py -c apps/imb/ --run --performance-report
"""

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.utility.sanity import defer
from pprint import pprint
import sys, os
from collections import namedtuple
from reframe.core.logging import getlogger
sys.path.append('.')
import modules
from modules.reframe_extras import ScalingTest

Metric = namedtuple('Metric', ['column', 'function', 'unit', 'label'])

class IMB_MPI1(rfm.RunOnlyRegressionTest):
    METRICS = []

    def __init__(self):
        self.valid_systems = ['*']
        self.valid_prog_environs = ['imb']
        self.exclusive_access = True
        self.perf_patterns = {} # must do this
        self.perf_patterns = {} # something funny about reframe's attr lookup
        self.executable = 'IMB-MPI1'
    
    # @rfm.run_before('run')
    def set_block_distribution(self):
        """ Ensure first half of processes are on first node
        
            TOOD: make conditional on using openmpi + srun
        """

        if any('openmpi' in m for m in self.current_partition.local_env.modules):
            launcher = self.job.launcher.registered_name
            if launcher == 'srun':
                self.job.launcher.options = ['--distribution=block']
            else:
                raise NotImplementedError('do not know how to set block distribution for launcher %r' % launcher )
        else:
            raise NotImplementedError('do not know how to set block distribution for partition %r' % self.current_partition.name )

    @rfm.run_before('run')
    def add_metrics(self):
        """ Create `self.perf_patterns` and units only in `self.reference`.
        
            Args:
                metrics: TODO
                n_procs: TODO
            
            TODO: Requires self.METRICS
        """
        
        for metric in self.METRICS:
            #getlogger().info('creating metric %s', metric.label)
            self.perf_patterns[metric.label] = reduce(self.stdout, self.num_tasks, metric.column, metric.function)
            self.reference[metric.label] = (0, None, None, metric.unit) # oddly we don't have to supply the "*" scope key??

    # @rfm.run_before('run')
    # def add_launcher_options(self):
    #     self.job.launcher.options = ['--report-bindings'] # note these are output to stdERR

@sn.sanity_function
def reduce(path, n_procs, column, function):
    """ Calculate an aggregate value from IMB output.

        Args:
            path: str, path to file
            n_procs: int, number of processes
            column: str, column name
            function: callable to apply to specified `column` of table for `n_procs` in `path`
    """
    tables = modules.imb.read_imb_out(path)
    table = tables[n_procs] # separate lines here for more useful KeyError if missing:
    col = table[column]
    result = function(col) 
    return result
    
@rfm.simple_test
class IMB_PingPong(IMB_MPI1):
    """ Runs on 2x cores of 2x nodes """
    METRICS = [
        # 'column' 'function', 'unit', 'label'
        Metric('Mbytes/sec', max, 'Mbytes/sec', 'max_bandwidth'),
        Metric('t[usec]', min, 't[usec]', 'min_latency'),
    ]
    def __init__(self):
        super().__init__()
        self.executable_opts = ['pingpong']
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        self.sanity_patterns = sn.assert_found('# Benchmarking PingPong', self.stdout)
        self.tags = {'pingpong'}

PROC_STEPS = [-1, -2, 0.25, 0.5, 0.75, 1.0]

@rfm.parameterized_test(*[[np] for np in PROC_STEPS])
class IMB_Uniband(IMB_MPI1, ScalingTest):
    """ Runs on varying numbers of processes from 2 up to physical cores of 2x nodes """
    METRICS = [
        Metric('Mbytes/sec', max, 'Mbytes/sec', 'max_bandwidth')
    ]
    def __init__(self, proc_step):
        """ proc_step: number of processes per node - see `modules.reframe_extras.ScalingTest.node_fraction`.
        """
        super().__init__()
        
        self.partition_fraction = -2 # 2x nodes only
        self.node_fraction = proc_step

        self.sanity_patterns = sn.assert_found('# Benchmarking Uniband', self.stdout)
        self.executable_opts = ['uniband', '-npmin', str(self.num_tasks)]
        self.tags = {'uniband'}
    
@rfm.parameterized_test(*[[np] for np in PROC_STEPS])
class IMB_Biband(IMB_MPI1, ScalingTest):  # NB: on alaska ib- fails with a timeout!
    """ Runs on varying numbers of processes from 2 up to physical cores of 2x nodes """
    METRICS = [
        Metric('Mbytes/sec', max, 'Mbytes/sec', 'max_bandwidth')
    ]
    def __init__(self, proc_step):
        """ proc_step: number of processes per node - see `modules.reframe_extras.ScalingTest.node_fraction`.
        """
        
        super().__init__()
        
        self.partition_fraction = -2 # 2x nodes only
        self.node_fraction = proc_step
        
        self.sanity_patterns = sn.assert_found('# Benchmarking Biband', self.stdout)
        self.executable_opts = ['biband', '-npmin', str(self.num_tasks)]
        self.tags = {'biband'}
        