""" Performance test using Intel MPI Benchmarks.

    Run using e.g.:
        
        cd hpc-tests
        conda activate hpc-tests
        reframe/bin/reframe -C reframe_config.py -c imb/ --run --performance-report

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
        self.add_metrics()
    
    def add_metrics(self):
        """ Add all Metrics from self.METRICS to performance/reference patterns """

        for metric in self.METRICS:
            self.perf_patterns[metric.label] = reduce(self.stdout, metric.column, metric.function)
            self.reference[metric.label] = (0, None, None, metric.unit) # oddly we don't have to supply the "*" scope key??

    # @rfm.run_before('run')
    # def add_launcher_options(self):
    #     self.job.launcher.options = ['--report-bindings'] # note these are output to stdERR

@sn.sanity_function
def reduce(path, column, function):
    data = modules.imb.read_imb_out(path)
    return function(data[column])

@rfm.simple_test
class IMB_PingPong(IMB_MPI1):
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
        
n_tasks = modules.reframe_extras.ntasks_param(cpu_factor=0.5) # because alaska has HT enabled TODO: add to config?


@rfm.parameterized_test(*[[n] for n in n_tasks]) 
class IMB_Uniband(IMB_MPI1):
    METRICS = [
        Metric('Mbytes/sec', max, 'Mbytes/sec', 'max_bandwidth')
    ]
    def __init__(self, num_cpus):
        super().__init__()
        self.executable_opts = ['uniband']
        self.num_tasks = num_cpus
        self.num_tasks_per_node = int(num_cpus / 2)
        self.sanity_patterns = sn.assert_found('# Benchmarking Uniband', self.stdout)
    
    @rfm.run_before('run')
    def add_launcher_options(self):
        self.job.launcher.options = ['--distribution=block'] # is default, but important here that 1st 1/2 of processes are on 1st node


@rfm.parameterized_test(*[[n] for n in n_tasks]) 
class IMB_Biband(IMB_MPI1):  # NB: on alaska -ib fails with a timeout!
    METRICS = [
        Metric('Mbytes/sec', max, 'Mbytes/sec', 'max_bandwidth')
    ]
    def __init__(self, num_cpus):
        super().__init__()
        self.executable_opts = ['biband']
        self.num_tasks = num_cpus
        self.num_tasks_per_node = int(num_cpus / 2)
        self.sanity_patterns = sn.assert_found('# Benchmarking Biband', self.stdout)

    @rfm.run_before('run')
    def add_launcher_options(self):
        self.job.launcher.options = ['--distribution=block'] # is default, but important here that 1st 1/2 of processes are on 1st node
