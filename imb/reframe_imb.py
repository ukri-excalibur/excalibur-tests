""" Performance test using Intel MPI Benchmarks.

    Run using e.g.:
        
        cd hpc-tests
        conda activate hpc-tests
        reframe/bin/reframe -C reframe_config.py -c imb/ --run --performance-report

    TODO: make latency log scale in notebook plots
    TODO: change output read to pandas.dataframe
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
# examples of output:
# # Benchmarking Uniband 
# # #processes = 2 
# #---------------------------------------------------
#        #bytes #repetitions   Mbytes/sec      Msg/sec
#             0         1000         0.00      2189915
#
# # Benchmarking PingPong 
# # #processes = 2 
# #---------------------------------------------------
#        #bytes #repetitions      t[usec]   Mbytes/sec
#             0         1000         2.25         0.00


Metric = namedtuple('Metric', ['benchmark', 'function', 'column', 'label'])

def read_imb_out(path):
    """ Read stdout from an IMB-MPI1 run. Note this may only contain ONE benchmark.
        
        Returns a dict with keys:
            
            'data': {
                    <column_heading1>: [value0, value1, ...],
                    ...,
                }
            'meta':
                'processes':num processes as int
                'benchmark': str, as above
                'path': str
    
        TODO: use numpy instead?
    """

    COLTYPES = {
        'uniband':(int, int, float, int),
        'biband':(int, int, float, int),
        'pingpong':(int, int, float, float),
    }

    result = {
        'meta': modules.utils.parse_path_metadata(path),
        'data': {},
        }
    with open(path) as f:
        for line in f:
            if line.startswith('# Benchmarking '):
                benchmark = line.split()[-1].lower()
                if 'benchmark' in result['meta']:
                    raise ValueError('%s may only contain one benchmark, found both %r and %r' % (result['meta']['benchmark'], benchmark))
                result['meta']['benchmark'] = benchmark
                col_types = COLTYPES[benchmark]
                result['meta']['processes'] = int(next(f).split()[-1]) # "# #processes = 2"
                next(f) # skip header
                while True:
                    cols = next(f).split()
                    if cols == []:
                        break
                    if cols[0].startswith('#'): # header row
                        header = cols
                        for label in header:
                            result['data'][label] = []
                    else:
                        for label, opr, value in zip(header, col_types, cols):
                            result['data'][label].append(opr(value))
    return result

@sn.sanity_function
def reduce(path, column, function):
    """ Reduce results along a particular column.

        Args:
            path: str, path to results file
            column: str, column of output to operate on, e.g. 'Mbytes/sec'
            function: function to apply to column values
        
        Example:
            reduce(self.stdout, 'pingpong', 'Mbytes/sec', max)

        Caches the result of reading the results file for efficency.
    """
    cache = getattr(reduce, 'cache', {})
    results = cache.setdefault(path, read_imb_out(path))
    values = results['data'][column]
    return function(values)

class IMB_MPI1(rfm.RunOnlyRegressionTest):
    METRICS = []

    def __init__(self):
        self.valid_systems = ['*']
        self.valid_prog_environs = ['imb']
        self.executable = 'IMB-MPI1'
        self.exclusive_access = True
        self.perf_patterns = {} # must do this
        #self.reference['*'] = {} # don't do this ...
        # self.reference = {'*':{}} # or this
        self.add_metrics()
    
    def add_metrics(self):
        """ TODO: """

        for metric in self.METRICS:
            benchmark = metric.benchmark.lower() # TODO: is this common across tests??
            perf_label = '_'.join((benchmark, metric.function.__name__, metric.label))
            self.perf_patterns[perf_label] = reduce(self.stdout, metric.column, metric.function)
            self.reference[perf_label] = (0, None, None, metric.column) # oddly we don't have to supply the "*" scope key??
        
    # @rfm.run_before('run')
    # def add_launcher_options(self):
    #     self.job.launcher.options = ['--report-bindings'] # note these are output to stdERR


@rfm.simple_test
class IMB_PingPong(IMB_MPI1):
    METRICS = [
        Metric(benchmark='pingpong', function=max, column='Mbytes/sec', label='bandwidth'),
        Metric(benchmark='pingpong', function=min, column='t[usec]', label='latency'),
    ]
    def __init__(self):
        super().__init__()
        self.executable_opts = ['pingpong']
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        self.sanity_patterns = sn.assert_found('# Benchmarking PingPong', self.stdout)
        
@rfm.simple_test
class IMB_Uniband(IMB_MPI1):
    METRICS = [
        Metric(benchmark='uniband', function=max, column='Mbytes/sec', label='bandwidth')
    ]
    def __init__(self):
        super().__init__()
        self.executable_opts = ['uniband']
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        self.sanity_patterns = sn.assert_found('# Benchmarking Uniband', self.stdout)
        
@rfm.simple_test # note -ib fails with a timeout!
class IMB_Biband(IMB_MPI1):
    METRICS = [
        Metric('biband', max, 'Mbytes/sec', 'bandwidth')
    ]
    def __init__(self):
        super().__init__()
        self.executable_opts = ['biband']
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        self.sanity_patterns = sn.assert_found('# Benchmarking Biband', self.stdout)
