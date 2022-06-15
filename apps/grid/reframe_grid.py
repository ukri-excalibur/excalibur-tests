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

    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 20

    variables = {
        'OMP_NUM_THREADS': f'{num_cpus_per_task}',
    }
    extra_resources = {
        'mpi': {'num_slots': num_tasks * num_cpus_per_task}
    }

    reference = {
        'csd3:icelake': {
            'Performance': (228286, None, None, 'Mflop/s per node')
        },
        '*': {
            'Performance': (150000, None, None, 'Mflop/s per node'),
        }
    }


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
    time_limit = '20m'

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
