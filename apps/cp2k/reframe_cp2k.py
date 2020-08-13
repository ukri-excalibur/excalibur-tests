""" Performance test using CP2K quantum chemistry and solid state physics software package for atomistic simulations.

    See README.md for details.

    NB:
    - The executable is either cp2k.popt (for MPI only) or cp2k.psmp (for MPI + OpenMP).
    - Only the former is currently implemented here.
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
        
        # these are the ones reframe uses:
        self.num_tasks_per_node = Scheduler_Info().pcores_per_node
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        self.tags = {'num_procs=%i' % self.num_tasks, 'num_nodes=%i' % self.num_nodes}
        
        self.exclusive_access = True
        self.time_limit = None
        
        # sanity patterns defined in superclass

        self.perf_patterns = {
            # from cp2k output:
            'cp2k_time': sn.extractsingle(r'^ CP2K\s+\d+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+([\d.]+)',
                                     self.stdout, 1, float), # "Total Max" time for CP2K subroutine
            # from `time`:
            'runtime_real': sn.extractsingle(r'^real\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time_cmd),
        }
        self.reference = {
            '*': {
                'cp2k_time': (0, None, None, 's'),
                'runtime_real': (0, None, None, 's'),
            }
        }