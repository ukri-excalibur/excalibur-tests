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
    - ONLY POPT IMPLEMENTED HERE

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
# want to use a module supplied as part of the reframe git repo:
RFM_CP2K_PATH = os.path.join('reframe', 'cscs-checks', 'apps', 'cp2k')
sys.path.append(RFM_CP2K_PATH)
from cp2k_check import Cp2kCheck as Rfm_Cp2kCheck

node_seq = sequence(1, Scheduler_Info().num_nodes + 1, 2)

@rfm.parameterized_test(*[[n_nodes] for n_nodes in node_seq])
class Cp2k_H2O_256(Rfm_Cp2kCheck):

    def __init__(self, num_nodes):
        
        super().__init__()
        
        # override not appropriate values in superclass:
        self.valid_systems = ['*']
        self.valid_prog_environs = ['cp2k']
        self.modules = []
        self.extra_resources = {}
        self.pre_run = ['time \\']
        self.executable = 'cp2k.popt'
        self.sourcesdir = os.path.join(os.path.abspath(RFM_CP2K_PATH), 'src')

        self.num_nodes = num_nodes
        self.tags = set([str(num_nodes)])

        # these are the ones reframe uses:
        self.num_tasks_per_node = Scheduler_Info().pcores_per_node
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        
        self.exclusive_access = True
        self.time_limit = None
        
        # sanity patterns defined in superclass

        self.perf_patterns = {
            # from cp2k output:
            'cp2k_time': sn.extractsingle(r'^ CP2K\s+\d+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+([\d.]+)',
                                     self.stdout, 1, float), # "Total Max" time for CP2K subroutine
            # from `time`:
            'runtime_real': sn.extractsingle(r'^real\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time_cmd),
            'runtime_user': sn.extractsingle(r'^user\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time_cmd),
            'runtime_sys': sn.extractsingle(r'^sys\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time_cmd),
        }
        self.reference = {
            '*': {
                'cp2k_time': (0, None, None, 's'),
                'runtime_real': (0, None, None, 's'),
                'runtime_user': (0, None, None, 's'),
                'runtime_sys': (0, None, None, 's'),
            }
        }