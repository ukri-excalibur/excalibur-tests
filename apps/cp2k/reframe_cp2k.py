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

class Cp2kBaseBenchmark(rfm.RegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['*']
    build_system = 'Spack'
    spack_spec = variable(str, value='cp2k@9.1')
    executable = 'cp2k.psmp'
    time_limit = '60m'
    num_cpus_per_task = 2
    num_tasks = required
    num_tasks_per_node = required

    @run_after('setup')
    def setup_num_tasks(self):
        self.set_var_default('num_tasks',
                             self.current_partition.processor.num_cpus // self.num_cpus_per_task)
        self.set_var_default('num_tasks_per_node', self.num_tasks)
        self.extra_resources = {
            'mpi': {'num_slots': self.num_tasks * self.num_cpus_per_task}
        }
        self.variables = {
            'OMP_NUM_THREADS': f'{self.num_cpus_per_task}',
            'OMP_PLACES': 'cores',
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
            'Maximum total time':
            sn.extractsingle(r'CP2K +([0-9]+) +([0-9.]+) +([0-9.]+) +([0-9.]+) +([0-9.]+) +([0-9.]+)', self.stdout, 6, float)
        }


@rfm.simple_test
class Cp2kH2O64Benchmark(Cp2kBaseBenchmark):
    sourcesdir = path.join(path.dirname(__file__), 'input-h2o_64')
    executable_opts = ['-i', 'H2O-64.inp']
    reference = {
        'cosma8': {
            'Maximum total time': (25, None, 0.2, 'seconds'),
        },
        '*': {
            'Maximum total time': (200, None, None, 'seconds'),
        }
    }


@rfm.simple_test
class Cp2kLiH_HFXBenchmark(Cp2kBaseBenchmark):
    sourcesdir = path.join(path.dirname(__file__), 'input-lih-hfx')
    executable_opts = ['-i', 'input_bulk_B88_3.inp']
    reference = {
        '*': {
            'Maximum total time': (200, None, None, 'seconds'),
        }
    }
