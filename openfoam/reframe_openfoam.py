""" Motorbike benchmark using OpenFOAM.

    See README.md for details.

    Run using e.g.:

        reframe/bin/reframe -C reframe_config.py -c openfoam/ --run --performance-report
    
    Run on a specific number of nodes by appending:

        --tag N
    
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
        self.executable = 'simpleFoam'
        self.executable_opts = []
        self.exclusive_access = True
        self.time_limit = None

        self.pre_run = [
            'cp -r $FOAM_TUTORIALS/incompressible/simpleFoam/motorBike/* .',
            # control domain decomposition:
            # using scotch method means simpleCoeffs is ignored so don't need to match num_tasks:
            'sed -i -- "s/method .*/method          scotch;/g" system/decomposeParDict'
            'sed -i -- "s/numberOfSubdomains .*/numberOfSubdomains %i;/g" system/decomposeParDict' % self.num_tasks,

            '. $WM_PROJECT_DIR/bin/tools/RunFunctions',
            'blockMesh',
            'decomposePar'
        ]
        # could also check:
        #$ ompi_info -c | grep -oE "MPI_THREAD_MULTIPLE[^,]*"
        # MPI_THREAD_MULTIPLE: yes

        self.post_run = ['reconstructPar']

        self.keep_files = [] # TODO:

        self.sanity_patterns = sn.assert_found(r'.*', self.stdout)
