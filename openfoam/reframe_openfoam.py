""" Motorbike benchmark using OpenFOAM.

    See README.md for details.

    Run using e.g.:

        reframe/bin/reframe -C reframe_config.py -c openfoam/ --run --performance-report
    
    Run on a specific number of nodes by appending:

        --tag 'N$'
    
    where N must be one of 1, 2, 4, ..., etc.
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

def parse_time(s):
    """ Convert timing info from `time` into float seconds.

       E.g. parse_time('0m0.000s') -> 0.0
    """

    mins, _, secs = s.partition('m')
    mins = float(mins)
    secs = float(secs.rstrip('s'))

    return mins * 60.0 + secs

@rfm.parameterized_test(*[[n_nodes] for n_nodes in node_seq])
class Openfoam_Mbike(rfm.RunOnlyRegressionTest):

    def __init__(self, num_nodes):
        
        self.valid_systems = ['*']
        self.valid_prog_environs = ['openfoam']
        
        self.num_nodes = num_nodes
        self.tags = set([str(num_nodes)])

        # these are the ones reframe uses:
        self.num_tasks_per_node = Scheduler_Info().pcores_per_node
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        
        #self.sourcesdir = '$FOAM_TUTORIALS'
        self.exclusive_access = True
        self.time_limit = None

        # NB: the pre_run commands actually do the MPI runs here
        self.pre_run = [
            'cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/motorBike/* .', # FOAM_TUTORIALS set by module
            './Allclean', # removes logs, old timehistories etc
            
            # set domain decomposition:
            # using 'scotch' method means simpleCoeffs is ignored so it doesn't need to match num_tasks:
            'sed -i -- "s/method .*/method          scotch;/g" system/decomposeParDict',
            'sed -i -- "s/numberOfSubdomains .*/numberOfSubdomains %i;/g" system/decomposeParDict' % self.num_tasks,

            'time ./Allrun', # actually runs steps of analysis
        ]
        # could also check:
        #$ ompi_info -c | grep -oE "MPI_THREAD_MULTIPLE[^,]*"
        # MPI_THREAD_MULTIPLE: yes

        # define a no-op to keep reframe happy:
        self.executable = 'hostname'
        self.executable_opts = []
        
        self.post_run = []

        self.keep_files = [
            'log.potentialFoam', 'log.snappyHexMesh', 'log.blockMesh', 'log.reconstructPar', 'log.surfaceFeatures',
            'log.decomposePar', 'log.reconstructParMesh', 'log.patchSummary', 'log.simpleFoam',
                  ]

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

        self.perf_patterns = {
            'Allrun_realtime': sn.extractsingle(r'^real\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time),
        }
        self.reference = {
            '*': {
                'Allrun_realtime': (0, None, None, 's'),
            }
        }
