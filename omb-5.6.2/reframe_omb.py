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

OSU_TESTS = [
    {'name':'OMB_Bandwidth_2_Nodes', 'executable':'osu_bw', 'metric':{'column':'Bandwidth (MB/s)', 'function':max}},
    {'name':'OMB_Bandwidth_1_Node', 'executable':'osu_bw', 'metric':{'column':'Bandwidth (MB/s)', 'function':max}, 'num_tasks_per_node':2},
    {'name':'OMB_Latency_2_Nodes', 'executable':'osu_latency','metric':{'column':'Latency (us)', 'function':min}},
    {'name':'OMB_Latency_1_Node', 'executable':'osu_latency','metric':{'column':'Latency (us)', 'function':min}, 'num_tasks_per_node':2},
    {'name':'OMB_MPI_Alltoall_Latency_2_Nodes', 'executable':'osu_alltoall', 'metric':{'column':'Avg Latency(us)', 'function':min}},
    {'name':'OMB_MPI_Alltoall_Latency_1_Node', 'executable':'osu_alltoall', 'metric':{'column':'Avg Latency(us)', 'function':min}, 'num_tasks_per_node':2},
    #{'descr':'OMB MPI_Alltoall LatencyN:N', 'executable':'osu_alltoall', 'metric':{'column':'Avg Latency(us)', 'function':min}, 'num_tasks':8, 'num_tasks_per_node':4},
    {'name':'OMB_MPI_Allgather_Latency_2_Nodes', 'executable':'osu_allgather', 'metric':{'column':'Avg Latency(us)', 'function':min}},
    {'name':'OMB_MPI_Allreduce_Latency_2_Nodes', 'executable':'osu_allreduce', 'metric':{'column':'Avg Latency(us)', 'function':min}},
]

@rfm.parameterized_test(*OSU_TESTS)
class OMB_Test(rfm.RunOnlyRegressionTest):
    def __init__(self, **args):
        
        if 'name' not in args:
            raise KeyError("'name' must be provided in parameters")
        if ' ' in args['name']:
            raise ValueError('test names (%r) may not contain spaces' % args['name'])

        super().__init__()
        
        # define defaults:
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        self.exclusive_access = True
        self.valid_systems = ['*:compute']
        self.valid_prog_environs = ['*']
        
        # potentially override from parameters:
        self.__dict__.update(args)

        # other properties:
        self.modules = ['omb']
        
        # sanity:
        sanity_str = re.escape(self.metric['column'])
        self.sanity_patterns = sn.assert_found(sanity_str, self.stdout)

        # performance:
        perf_label = '%s_%s' % (self.metric['function'].__name__, self.metric['column'].rsplit('(')[0].strip())
        perf_units = self.metric['column'].rsplit('(')[-1].replace(')', '') # i.e. get bit out of brackets in last column
        self.perf_patterns = {
            perf_label: reduce_omb_out(self.stdout, self.metric['column'], self.metric['function']),
        }
        self.reference = { # TODO: could provide a helper as we'll always be doing this
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
