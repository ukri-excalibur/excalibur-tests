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
import sys, re

def read_omb_out(path):
    """ Read stdout from a 2-column OMB output file.
        
        TODO: Returns dict with keys ?? and 'file'.
        
        TODO: use numpy instead?
    """
    
    results = {'file': path,
               'data': {},
    }
    COL_TYPES = (int, float)
    
    with open(path) as f:
        for line in f:
            if line.startswith('# OSU'):
                continue
            elif line.startswith('#'):
                columns = line.strip().split(None, 2)[1:] # will get written twice!
                for col in columns:
                    results['data'][col] = []
                continue
            if line.strip() == '':
                continue
            values = [opr(v) for (opr, v) in zip(COL_TYPES, line.split())]
            assert len(values) == len(COL_TYPES), "len(values):%i len(COL_TYPES):%i line:%s" % (len(values), len(COL_TYPES), line)
            for ci, col in enumerate(columns):
                v = values[ci]
                results['data'][col].append(v)
    return results

@sn.sanity_function
def reduce_omb_out(path, column, func):
    results = read_omb_out(path) # TODO: caching
    try:
        axis = results['data'][column]
    except KeyError:
        raise KeyError('%r not found, have %s' % (column, results['data'].keys()))
    return func(axis)

class OMB_BaseTest(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.executable_opts = []
        self.descr = 'Base class for OSU Micro Benchmarks'
        self.valid_systems = ['sausage-newslurm:compute']
        self.valid_prog_environs = ['gnu8-openmpi3']
        self.sourcedir = None
        self.modules = ['omb']
        self.exclusive_access = True
        
OSU_TESTS = [
    {'descr':'OMB Bandwidth (intra-node)', 'executable':'osu_bw', 'metric':{'column':'Bandwidth (MB/s)', 'function':max}},
    {'descr':'OMB Bandwidth (in-node)', 'executable':'osu_bw', 'metric':{'column':'Bandwidth (MB/s)', 'function':max}, 'num_tasks_per_node':2},
    {'descr':'OMB Latency', 'executable':'osu_latency','metric':{'column':'Latency (us)', 'function':min}},
    {'descr':'OMB MPI_Alltoall Latency', 'executable':'osu_alltoall','metric':{'column':'Avg Latency(us)', 'function':min}, 'num_tasks':0, 'num_tasks_per_core':1},
    {'descr':'OMB MPI_Allgather Latency Test', 'executable':'osu_allgather', 'metric':{'column':'Avg Latency(us)', 'function':min}},
    {'descr':'OMB MPI_Allreduce Latency Test', 'executable':'osu_allreduce', 'metric':{'column':'Avg Latency(us)', 'function':min}},
    
]

@rfm.parameterized_test(*OSU_TESTS)
class OMB_GenericTest(OMB_BaseTest):
    def __init__(self, **args):
        super().__init__()

        # anything here can be overwritten by config dict:        
        self.num_tasks = 2
        self.num_tasks_per_node = 1

        self.__dict__.update(args)
        self.name = self.descr.replace(' ', '_')

        sanity_str = re.escape(self.metric['column'])
        self.sanity_patterns = sn.assert_found(sanity_str, self.stdout)
        perf_label = '%s_%s' % (self.metric['function'].__name__, self.metric['column'].rsplit('(')[0].strip())
        perf_units = self.metric['column'].rsplit('(')[-1].replace(')', '') # i.e. get bit out of brackets in last column
        self.perf_patterns = {
            perf_label: reduce_omb_out(self.stdout, self.metric['column'], self.metric['function']),
        }
        self.reference = {
            '*': {
                perf_label: (0, None, None, perf_units),
            }
        }
        

if __name__ == '__main__':
    # hacky test of extraction:
    from reframe.utility.sanity import evaluate
    # with open(sys.argv[-1]) as f:
    #     stdout = f.read()
    # pprint(evaluate(imb_results(stdout, 'Uniband')))
