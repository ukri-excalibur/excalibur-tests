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
from modules.utils import parse_time_cmd

node_seq = sequence(1, Scheduler_Info().num_nodes + 1, 2)

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
        
        self.sourcesdir = 'downloads'
        self.exclusive_access = True
        self.time_limit = None

        self.pre_run = [
            'tar --strip-components 2 -xf Motorbike_bench_template.tar.gz bench_template/basecase',
            './Allclean', # removes logs, old timehistories etc just in case 
            
            # set domain decomposition:
            # using 'scotch' method means simpleCoeffs is ignored so it doesn't need to match num_tasks:
            'sed -i -- "s/method .*/method          scotch;/g" system/decomposeParDict',
            'sed -i -- "s/numberOfSubdomains .*/numberOfSubdomains %i;/g" system/decomposeParDict' % self.num_tasks,

            # remove streamlines:
            'sed -i -- \'s/    #include "streamLines"//g\' system/controlDict',
            'sed -i -- \'s/    #include "wallBoundedStreamLines"//g\' system/controlDict',

            # fix location of mesh quality defaults (needed for v6+?)
            "sed -i -- 's|caseDicts|caseDicts/mesh/generation|' system/meshQualityDict",

            './Allmesh', # do meshing

            'time \\', # want to run mpi task under time
        ]
        # could also check:
        #$ ompi_info -c | grep -oE "MPI_THREAD_MULTIPLE[^,]*"
        # MPI_THREAD_MULTIPLE: yes

        self.executable = 'simpleFoam' # Duh this runs srun time - 
        self.executable_opts = ['-parallel']
        
        self.post_run = []

        self.keep_files = ['log.snappyHexMesh', 'log.blockMesh', 'log.decomposePar']

        result = sn.extractall(
            r'time step continuity errors : '
            r'\S+\s\S+ = \S+\sglobal = (?P<res>-?\S+),',
            self.stdout, 'res', float)
        # NB: `time` outputs to stderr so can't assume that should be empty
        self.sanity_patterns = sn.all([
            # ensure meshing finished ok:
            sn.assert_found('End', 'log.blockMesh'),
            sn.assert_found('End', 'log.decomposePar'),
            sn.assert_found('Finished meshing without any errors', 'log.snappyHexMesh'),
            
            # ensure simpleFoam finished ok:
            sn.assert_found('Finalising parallel run', self.stdout),
            sn.assert_not_found('FOAM FATAL ERROR', self.stdout),
            sn.assert_not_found('FOAM FATAL ERROR', self.stderr),
            
            # ensure continuity errors small enough - copied from
            # https://github.com/eth-cscs/reframe/blob/0a4dc5207b35c737861db346bd483fd4ac202846/cscs-checks/apps/openfoam/check_openfoam_extend.py#L56
            sn.all(
                sn.map(lambda x: sn.assert_lt(abs(x), 5.e-04), result)
            ),
        ])

        self.perf_patterns = {
            # from openfoam output:
            'ExecutionTime': sn.extractall(r'ExecutionTime = ([\d.]+) s  ClockTime = ([\d.]+) s', self.stdout, 1, float)[-1],
            'ClockTime': sn.extractall(r'ExecutionTime = ([\d.]+) s  ClockTime = ([\d.]+) s', self.stdout, 2, float)[-1],
            # from `time`:
            'runtime_real': sn.extractsingle(r'^real\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time_cmd),
            'runtime_user': sn.extractsingle(r'^user\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time_cmd),
            'runtime_sys': sn.extractsingle(r'^sys\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time_cmd),
        }
        self.reference = {
            '*': {
                'ExecutionTime': (0, None, None, 's'),
                'ClockTime': (0, None, None, 's'),
                'runtime_real': (0, None, None, 's'),
                'runtime_user': (0, None, None, 's'),
                'runtime_sys': (0, None, None, 's'),
            }
        }
