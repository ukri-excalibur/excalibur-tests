# Copyright 2022 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

"""
ReFrame benchmark for GIRD: https://github.com/paboyle/Grid

WARNING:
The code is Hybrid OpenMP + MPI with NUMA socket aware optimisations.
The relevant options can make big changes to delivered performance.
"""

import os.path as path
import sys

import reframe as rfm
import reframe.utility.sanity as sn
sys.path.append(path.join(path.dirname(__file__), '..', '..'))
from modules.utils import identify_build_environment

class GridBenchmark(rfm.RegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['*']
    build_system = 'Spack'
    spack_spec = variable(str, value='grid@develop')

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = [self.spack_spec]
        self.build_system.environment = identify_build_environment(
            self.current_partition)


@rfm.simple_test
class GridBenchmark_ITT(GridBenchmark):
    tags = {"ITT"}
    executable = 'Benchmark_ITT'
    executable_opts = ['--shm 1024 --shm-hugetlb']
    time_limit = '59m'

    num_cpus_per_task = required
    num_tasks = required
    num_tasks_per_node = required

    reference = {
        'cosma8': {
            'Performance': (425000, None, None, 'Mflop/s per node')
        },
        'csd3:icelake': {
            'Performance': (450000, None, None, 'Mflop/s per node')
        },
        'csd3:skylake': {
            'Performance': (22000, None, None, 'Mflop/s per node')
        },
        'dial3': {
            'Performance': (28000, None, None, 'Mflop/s per node')
        },
        'myriad': {
            'Performance': (350000, None, None, 'Mflop/s per node')
        },
        'tesseract': {
            'Performance': (250000, None, None, 'Mflop/s per node')
        },
        '*': {
            'Performance': (150000, None, None, 'Mflop/s per node'),
        }
    }

    @run_after('setup')
    def setup_num_tasks(self):
        self.set_var_default('num_cpus_per_task',
                             self.current_partition.processor.num_cpus)
        self.set_var_default('num_tasks', 1)
        self.set_var_default('num_tasks_per_node', 1)
        self.extra_resources = {
            'mpi': {'num_slots': self.num_tasks * self.num_cpus_per_task}
        }
        self.variables = {
            'OMP_NUM_THREADS': f'{self.num_cpus_per_task}',
            'OMP_PLACES': 'cores',
        }

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'Per Node Summary table',
                                               self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):
        """
        e.g.

        Grid : Message : 380809 ms :  Comparison point  result: 143382.7 Mflop/s per node
        """

        self.perf_patterns = {
            'Performance': sn.extractsingle(r'result: (\S+) Mflop/s per node',
                                            self.stdout, 1, float)
        }
