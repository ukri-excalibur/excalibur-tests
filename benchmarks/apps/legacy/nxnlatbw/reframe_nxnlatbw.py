""" Run a ping-pong latency test matrix between all nodes in the ReFrame partition.

    Usage:
    
        reframe/bin/reframe -C reframe_config.py -c apps/nxnlatbw/ --run
   
   NB: This is not a performance test in the ReFrame sense!
"""

import reframe as rfm
import reframe.utility.sanity as sn
import sys
sys.path.append('.')
from modules.reframe_extras import ScalingTest


@rfm.simple_test
class Nxnlatbw(ScalingTest):
    def __init__(self):

        self.valid_systems = ['-gpu']
        self.valid_prog_environs = ['nxnlatbw']

        self.build_system = 'SingleSource'
        self.sourcepath = 'mpi_nxnlatbw.c'

        self.partition_fraction = 1.0
        self.node_fraction = -1 # use 1x physical cores per node
        
        self.executable = 'nxnlatbw'
        self.exclusive_access = True
        self.time_limit = '1h'

        self.sanity_patterns = sn.assert_found(r'src,dst,lat\(us\),bandwidth\(\(Mbytes/sec\)', self.stdout)
