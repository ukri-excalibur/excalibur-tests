""" Performance test using IMB's uniband and biband.

    Run using something like:
        
        cd hpc-tests
        conda activate reframe
        reframe/bin/reframe -c imb-2018.1/ --run --performance-report

    Runs:
    - 2 tasks on same node
    - 2 tasks on different nodes
    Both have exclusive node access.
"""

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.utility.sanity import defer
from pprint import pprint
import sys

def read_imb_out(path):
    """ Read stdout from an IMB-MPI1 run.
        
        Returns nested dict with keys:
            <benchmark>:
                'data': {
                    <column_heading1>: [value0, value1, ...],
                    ...,
                }
                'name': benchmark name as str
                'params': ['processes':num processes as str]
        
        TODO: use numpy instead?
    """

    results = {'file':path}
    COL_TYPES = {'Uniband':(int, int, float, int),
                 'Biband':(int, int, float, int),
                }
    with open(path) as f:
        for line in f:
            if line.startswith('# Benchmarking '):
                benchmark = line.split()[-1]
                processes = next(f).split()[-1] # "# #processes = 2"
                result = {'name':benchmark, 'data':{}, 'params':{'processes':processes}}
                results[benchmark] = result
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
                        for label, opr, value in zip(header, COL_TYPES[benchmark], cols):
                            result['data'][label].append(opr(value))
    return results

@sn.sanity_function
def max_bandwidth(path, benchmark):
    results = read_imb_out(path) # TODO: caching
    bw = results[benchmark]['data']['Mbytes/sec']
    return max(bw)

@rfm.parameterized_test([1], [2])
class IMB_MPI1Test(rfm.RunOnlyRegressionTest):
    def __init__(self, num_nodes):
        self.name = self.name + "_Nodes" # default names for parameterised tests include argument(s)
        self.valid_systems = ['*']
        self.valid_prog_environs = ['*']
        self.modules = ['imb']
        self.executable = 'IMB-MPI1' # mpirun --mca btl_base_warn_component_unused 0 IMB-MPI1 uniband biband
        self.executable_opts = ['uniband', 'biband'] # TODO: use parameterised test instead??
        self.sanity_patterns = sn.all([sn.assert_found('# Benchmarking %s' % b.capitalize(), self.stdout) for b in self.executable_opts])
        self.perf_patterns = {
            'uniband_max_bandwidth': max_bandwidth(self.stdout, 'Uniband'),
            'biband_max_bandwidth': max_bandwidth(self.stdout, 'Biband'),
        }
        self.reference = {
            '*': {
                'uniband_max_bandwidth': (0, None, None, 'Mbytes/sec'),
                'biband_max_bandwidth': (0, None, None, 'Mbytes/sec'),
            }
        }
        self.exclusive_access = True
        self.num_tasks = 2
        self.num_tasks_per_node = int(self.num_tasks / num_nodes)


if __name__ == '__main__':
    # hacky test of extraction:
    from reframe.utility.sanity import evaluate
    # with open(sys.argv[-1]) as f:
    #     stdout = f.read()
    # pprint(evaluate(imb_results(stdout, 'Uniband')))
