# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import reframe as rfm
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest


@rfm.simple_test
class HpgmgTest(SpackTest):
    valid_systems = ['*']
    valid_prog_environs = ['default']
    spack_spec = 'hpgmg@0.4'
    executable = 'hpgmg-fv'
    executable_opts = ['7', '8']
    num_tasks = 4
    num_tasks_per_node = 4
    num_cpus_per_task = 4
    time_limit = '30m'
    reference = {
        '*': {
            'l_0': (1e8, -0.9, 0.6, 'DOF/s'),
            'l_1': (1e8, -0.9, 0.6, 'DOF/s'),
            'l_2': (1e8, -0.9, 0.6, 'DOF/s'),
        }
    }

    @run_after('setup')
    def setup_variables(self):
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'
        self.env_vars['OMP_PLACES'] = 'cores'
        self.extra_resources = {
            'mpi': {'num_slots': self.num_tasks * self.num_cpus_per_task}
        }

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'HPGMG-FV Benchmark',
                                               self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):
        dofs = sn.extractall(r'DOF/s=(\S+)\s+.*',
                             self.stdout, 1, float)
        self.perf_patterns = {
            'l_0': dofs[0],
            'l_1': dofs[1],
            'l_2': dofs[2],
        }
