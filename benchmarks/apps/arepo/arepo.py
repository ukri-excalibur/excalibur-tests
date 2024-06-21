# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import reframe as rfm
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest
import os.path as path

@rfm.simple_test
class ArepoBenchmark(SpackTest):
    valid_systems = ['-gpu']
    valid_prog_environs = ['default']
    spack_spec = 'arepo@master'  
    num_tasks = 4
    num_tasks_per_node = 1
    num_cpus_per_task = 1
    sourcesdir = path.join(path.dirname(__file__), 'input')
    executable = 'Arepo' 
    time_limit = '20m'
    reference = {
        'cosma8': {
            'duration': (40, None, 0.2, 'seconds'),
        },
        '*': {
            'duration': (200, None, None, 'seconds'),
        },
    }
    
    @run_after('setup')
    def setup_variables(self):
        self.executable_opts = ['param.txt']  
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'bye!', self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):
        self.perf_patterns = {
        'duration': sn.extractsingle(
            r'Code run for (\S+) seconds!',
            self.stdout, 1, float),
    }
    
