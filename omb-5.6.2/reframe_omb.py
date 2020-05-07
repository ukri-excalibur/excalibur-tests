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

# def read_omb_bw_out(path):
#     """ Read stdout from an osu_bw run.
        
#         Returns dict with keys 'data.size', 'data.bandwidth' and 'file'.
        
#         TODO: use numpy instead?
#     """

#     results = {'file':path,
#                'data':{
#                     'size':[],
#                     'bandwidth':[],
#                 },
#     }
#     COL_TYPES = (int, float)
#     with open(path) as f:
#         for line in f:
#             if line.startswith('#'):
#                 continue
#             values = [opr(v) for (opr, v) in zip(COL_TYPES, line.split())]
#             results['data']['size'].append(values[0])
#             results['data']['bandwidth'].append(values[1])
#     return results

def read_omb_bw_out(path, columns):
    """ Read stdout from an osu_bw run.
        
        Returns dict with keys 'data.size', 'data.bandwidth' and 'file'.
        
        TODO: use numpy instead?
    """
    
    results = {'file': path,
               'data': dict((c, list()) for c in columns),
    }
    COL_TYPES = (int, float)
    assert len(COL_TYPES) == len(columns)
    assert len(COL_TYPES) == len(results['data'])

    with open(path) as f:
        for line in f:
            if line.startswith('#') or line.strip() == '':
                continue
            values = [opr(v) for (opr, v) in zip(COL_TYPES, line.split())]
            assert len(values) == len(COL_TYPES), "len(values):%i len(COL_TYPES):%i line:%s" % (len(values), len(COL_TYPES), line)
            for ci, col in enumerate(columns):
                v = values[ci]
                results['data'][col].append(v)
    return results


@sn.sanity_function
def max_bandwidth(path):
    results = read_omb_bw_out(path) # TODO: caching
    bw = results['data']['bandwidth']
    return max(bw)

@sn.sanity_function
def generic_max(path, columns):
    results = read_omb_bw_out(path, columns)# TODO: caching
    axis = results['data'][columns[-1]]
    return max(axis)


class OMB_BaseTest(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.executable_opts = []
        self.descr = 'Base class for OSU Micro Benchmarks'
        self.valid_systems = ['sausage-newslurm:compute']
        self.valid_prog_environs = ['gnu8-openmpi3']
        self.sourcedir = None
        self.modules = ['omb']
        
#@rfm.simple_test
class OMB_BWTest(OMB_BaseTest):
    def __init__(self):
        super().__init__()
        self.descr = 'osu_bw: Bandwidth Test'
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

#@rfm.simple_test
class OMB_LatencyTest(OMB_BaseTest):
    def __init__(self):
        super().__init__()
        self.descr = 'osu_latency: Latency Test'
        self.executable = 'osu_latency'
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


# TODO: add 'metric' field taking column name and function (min, max, etc)
OSU_TESTS = [
    #{'descr':'Bandwidth', 'executable':'osu_bw',     'columns':('Size', 'Bandwidth (MB/s)')},
    #{'descr':'Latency', 'executable':'osu_latency','columns':('Size', 'Latency (us)')},
    {'descr':'MPI_Alltoall Latency', 'executable':'osu_alltoall','columns':('Size', 'Avg Latency(us)'),},
    
]

@rfm.parameterized_test(*OSU_TESTS)
class OMB_GenericTest(OMB_BaseTest):
    def __init__(self, **args):
        super().__init__()
        self.__dict__.update(args)

        sanity_str = re.escape(self.columns[-1])
        #sanity_str = re.escape(self.descr.split()[-1])
        self.sanity_patterns = sn.assert_found(sanity_str, self.stdout)
        perf_label = 'max_%s' % self.columns[-1].split()[0]
        perf_units = self.columns[-1].rsplit('(')[-1].replace(')', '') # i.e. get bit out of brackets in last column
        self.perf_patterns = {
            perf_label: generic_max(self.stdout, self.columns),
        }
        self.reference = {
            '*': {
                perf_label: (0, None, None, perf_units),
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
