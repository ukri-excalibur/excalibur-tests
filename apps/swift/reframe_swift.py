# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os.path as path
import sys
import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(path.join(path.dirname(__file__), '..', '..'))
from modules.utils import identify_build_environment

@rfm.simple_test
class SwiftBenchmark(rfm.RegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['*']
    build_system = 'Spack'
    spack_spec = variable(str, value='swiftsim@0.9.0')
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 1
    executable = 'swift'
    executable_opts = ['--help']
    time_limit = '2m'
    variables = {
        'OMP_NUM_THREADS': f'{num_cpus_per_task}',
    }
    extra_resources = {
        'mpi': {'num_slots': num_tasks * num_cpus_per_task}
    }

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = [self.spack_spec]
        self.build_system.environment = identify_build_environment(
            self.current_partition)

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'Version : 0.9.0', self.stdout)
