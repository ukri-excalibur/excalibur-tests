""" TODO:

    See README.md for details.

    Run using e.g.:

        reframe/bin/reframe -C reframe_config.py -c cp2k/ --run --performance-report
    
    Run on a specific number of nodes by appending:

        --tag 'N$'
    
    where N must be one of 1, 2, 4, ..., etc.


    TODO: DELETE THIS:
    NOTES:
    - want cp2k.popt (for MPI only ) or .psmp (for MPI + OpenMP)

"""

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.utility.sanity import defer
from pprint import pprint
import sys, os
from collections import namedtuple
from reframe.core.logging import getlogger
sys.path.append('.')
from modules.reframe_extras import sequence, Scheduler_Info, CachedRunTest

node_seq = sequence(1, Scheduler_Info().num_nodes + 1, 2)

@rfm.parameterized_test(*[[n_nodes] for n_nodes in node_seq])
class Cp2k(rfm.RunOnlyRegressionTest):

    def __init__(self, num_nodes):
        

        self.project = 'H2O-128' # TODO: could extract this in child class
        self.inp = '%s.inp' % self.project

        self.valid_systems = ['*']
        self.valid_prog_environs = ['cp2k']
        
        self.num_nodes = num_nodes
        self.tags = set([str(num_nodes)])

        # these are the ones reframe uses:
        self.num_tasks_per_node = Scheduler_Info().pcores_per_node
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        
        self.exclusive_access = True
        self.time_limit = None

        self.pre_run = [
            # get benchmark files:
            'wget https://raw.githubusercontent.com/misteliy/cp2k/master/tests/QS/benchmark/%s' % self.inp, # TODO: this is master, is this what we want??
            'wget https://raw.githubusercontent.com/misteliy/cp2k/master/tests/QS/GTH_BASIS_SETS',
            'wget https://raw.githubusercontent.com/misteliy/cp2k/master/tests/QS/POTENTIAL',
            # modify input deck to account for flat staging directory:
            'sed -i -- "s/    BASIS_SET_FILE_NAME ..\/GTH_BASIS_SETS/    BASIS_SET_FILE_NAME GTH_BASIS_SETS/g" %s' % self.inp,
            'sed -i -- "s/    POTENTIAL_FILE_NAME ..\/POTENTIAL/    POTENTIAL_FILE_NAME POTENTIAL/g" %s' % self.inp,
        ]
        
        self.executable = 'cp2k.popt'
        self.executable_opts = [self.inp]
        
        #self.keep_files = []  # TODO

        # TODO:
        result = sn.extractall(
            r'time step continuity errors : '
            r'\S+\s\S+ = \S+\sglobal = (?P<res>-?\S+),',
            self.stdout, 'res', float)
        # NB: `time` outputs to stderr so can't assume that should be empty
        self.sanity_patterns = sn.all([
            # ensure simpleFoam finished:
            sn.assert_found('Finalising parallel run', 'log.simpleFoam'),
            sn.assert_not_found('FOAM FATAL ERROR', 'log.simpleFoam'),
            # ensure continuity errors small enough - copied from
            # https://github.com/eth-cscs/reframe/blob/0a4dc5207b35c737861db346bd483fd4ac202846/cscs-checks/apps/openfoam/check_openfoam_extend.py#L56
            sn.all(
                sn.map(lambda x: sn.assert_lt(abs(x), 5.e-04), result)
            ),
        ])

        # TODO:
        # self.perf_patterns = {
        #     'Allrun_realtime': sn.extractsingle(r'^real\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time),
        # }
        # self.reference = {
        #     '*': {
        #         'Allrun_realtime': (0, None, None, 's'),
        #     }
        # }
