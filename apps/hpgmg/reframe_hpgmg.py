# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
import os.path as path
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class HpgmgTest(rfm.RegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['*']
    build_system = 'Spack'
    executable = 'hpgmg-fv'
    executable_opts = ['7', '8']
    num_tasks = 4
    num_cpus_per_task = 4
    time_limit = '30m'
    variables = {
        'OMP_NUM_THREADS': f'{num_cpus_per_task}',
        'OMP_PLACES': 'cores'
    }
    reference = {
        '*': {
            'l_0': (1e8, -0.9, 0.6, 'DOF/s'),
            'l_1': (1e8, -0.9, 0.6, 'DOF/s'),
            'l_2': (1e8, -0.9, 0.6, 'DOF/s'),
        }
    }
    extra_resources = {
        'mpi': {'num_slots': num_tasks * num_cpus_per_task}
    }

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = ['hpgmg@0.4']
        # Select the Spack environment:
        # * if `EXCALIBUR_SPACK_ENV` is set, use that one
        # * if not, use a provided spack environment for the current system
        # * if that doesn't exist, default to `None` and let ReFrame
        #   automatically create a minimal environment
        # TODO: this snippet should be in a utility function that all tests will
        # use
        if os.getenv('EXCALIBUR_SPACK_ENV'):
            self.build_system.environment = os.getenv('EXCALIBUR_SPACK_ENV')
        else:
            env = path.realpath(
                path.join(path.dirname(__file__), '..', '..', 'spack-environments',
                          self.current_system.name)
            )
            if path.isdir(env):
                self.build_system.environment = env
            else:
                self.build_system.environment = None

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
