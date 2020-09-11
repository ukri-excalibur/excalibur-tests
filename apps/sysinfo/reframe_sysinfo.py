""" Gather system information from all nodes in a (ReFrame) partition

    reframe/bin/reframe -C reframe_config.py -c apps/sysinfo/ --run
"""

import reframe as rfm
import reframe.utility.sanity as sn
from reframe.utility.sanity import defer
from pprint import pprint
import sys, os, glob, json
from collections import namedtuple
from reframe.core.logging import getlogger
sys.path.append('.')
from modules.reframe_extras import sequence, Scheduler_Info, CachedRunTest
from modules.utils import parse_time_cmd
from modules.sysinfo import sysinfo

@rfm.simple_test
class Sysinfo(rfm.RunOnlyRegressionTest):

    def __init__(self):
        
        self.valid_systems = ['*']
        self.valid_prog_environs = ['sysinfo']
        
        self.num_nodes = Scheduler_Info().num_nodes

        # these are the ones reframe uses:
        self.num_tasks_per_node = 1
        self.num_tasks = self.num_nodes * self.num_tasks_per_node
        
        self.sourcesdir = '../../modules/sysinfo'
        self.exclusive_access = False

        #self.pre_run = []
        
        self.executable = 'python'
        self.executable_opts = ['sysinfo.py']
        
        self.post_run = [
            #'cat *.sysinfo.json > all.info.json', # just for debugging
            'echo Done',
            ]

        self.keep_files = ['sysinfo.json'] # see self.collate()

        self.sanity_patterns = sn.assert_found('Done', self.stdout) # TODO: assert stderr is empty

    @rfm.run_after('run')
    def collate(self):
        """ Collate $HOSTNAME.sysinfo.json files into a single file - because `post_run` doesn't support globbing. """

        # read all files into a single dict:
        allhosts = {} # key-> hostname, value->{}
        for hostfile in glob.glob(os.path.join(self.stagedir, '*.sysinfo.json')):
            with open(hostfile) as infile:
                hostinfo = json.load(infile)
            hostname = hostinfo['hostname']
            allhosts[hostname] = hostinfo
        if len(allhosts) == 0:
            raise ValueError('No *.sysinfo.json files found.')
        
        # write them out:
        outpath = os.path.join(self.stagedir, 'sysinfo.json')
        with open(outpath, 'w') as outfile:
            json.dump(allhosts, outfile, indent=2)
