""" Gather system information from all nodes in a (ReFrame) partition

    reframe/bin/reframe -C reframe_config.py -c apps/sysinfo/ --run
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

@rfm.simple_test
class Sysinfo(rfm.RunOnlyRegressionTest):

    def __init__(self):
        
        self.valid_systems = ['*']
        self.valid_prog_environs = ['sysinfo']
        
        self.num_nodes = Scheduler_Info().num_nodes

        # these are the ones reframe uses:
        self.num_tasks_per_node = 1
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        #self.tags = {'num_procs=%i' % self.num_tasks, 'num_nodes=%i' % self.num_nodes}
        
        self.sourcesdir = '../../modules/sysinfo'
        self.exclusive_access = False

        #self.pre_run = []
        
        self.executable = 'python' # Duh this runs srun time - 
        self.executable_opts = ['sysinfo.py']
        
        self.post_run = [
            'cat *.sysinfo.json > all.info.json',
            'python summarise.py',
            'echo Done',
            ]

        self.keep_files = ['sysinfo.json']

        self.sanity_patterns = sn.assert_found('Done', self.stdout)
