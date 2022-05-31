# Copyright 2022 University College London (UCL) Research Software Development
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
class Cp2kH2O64Benchmark(rfm.RegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['*']
    build_system = 'Spack'
    spack_spec = variable(str, value='cp2k@9.1')
    num_tasks = 12
    num_tasks_per_node = num_tasks
    num_cpus_per_task = 2
    sourcesdir = path.join(path.dirname(__file__), 'input-h2o_64')
    executable = 'cp2k.psmp'
    executable_opts = ['-i', 'H2O-64.inp']
    time_limit = '60m'
    variables = {
        'OMP_NUM_THREADS': f'{num_cpus_per_task}',
        'OMP_PLACES': 'cores',
    }
    extra_resources = {
        'mpi': {'num_slots': num_tasks * num_cpus_per_task}
    }
    reference = {
        '*': {
            'Total time': (200, None, None, 'seconds'),
        }
    }

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = [self.spack_spec]
        self.build_system.environment = identify_build_environment(
            self.current_partition)

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'T I M I N G', self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):
        self.perf_patterns = {
            'Total time':
            sn.extractsingle(r'CP2K +(\S+) +(\S+) +(\S+) +(\S+) +(\S+) +(\S+)', self.stdout, 6, float)
        }
