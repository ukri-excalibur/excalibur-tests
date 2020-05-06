""" Performance test using OSU's Micro Benchmarks (OMB).

    Run using something like:
        
        cd hpc-tests
        conda activate reframe
        reframe/bin/reframe -c omb-5.6.2/ -R --run --performance-report

 TODO:
 - parameterise to different numbers of nodes/jobs-per-node

"""

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.utility.sanity import defer
from pprint import pprint
import sys

def read_omb_bw_out(path):
    """ Read stdout from an osu_bw run.
        
        Returns dict with keys 'data.size', 'data.bandwidth' and 'file'.
        
        TODO: use numpy instead?
    """

    results = {'file':path,
               'data':{
                    'size':[],
                    'bandwidth':[],
                },
    }
    COL_TYPES = (int, float)
    with open(path) as f:
        for line in f:
            if line.startswith('#'):
                continue
            values = [opr(v) for (opr, v) in zip(COL_TYPES, line.split())]
            results['data']['size'].append(values[0])
            results['data']['bandwidth'].append(values[1])
    return results

@sn.sanity_function
def max_bandwidth(path):
    results = read_omb_bw_out(path) # TODO: caching
    bw = results['data']['bandwidth']
    return max(bw)

@rfm.simple_test
class OMB_BWTest(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Test of using reframe to run OSU Bandwidth'
        self.valid_systems = ['sausage-newslurm:compute']
        self.valid_prog_environs = ['gnu8-openmpi3']
        self.sourcedir = None
        self.modules = ['omb']
        self.executable = 'osu_bw'
        self.executable_opts = []
        self.sanity_patterns = sn.assert_found(r'OSU MPI Bandwidth Test', self.stdout)
        self.perf_patterns = {
            'max_bandwidth': max_bandwidth(self.stdout),
        }
        self.reference = {
            '*': {
                'max_bandwidth': (0, None, None, 'Mbytes/sec'),
            }
        }
        self.num_tasks = 2
        self.num_tasks_per_node = 1

if __name__ == '__main__':
    # hacky test of extraction:
    from reframe.utility.sanity import evaluate
    # with open(sys.argv[-1]) as f:
    #     stdout = f.read()
    # pprint(evaluate(imb_results(stdout, 'Uniband')))
