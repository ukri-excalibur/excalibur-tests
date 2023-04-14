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

from functools import reduce
from operator import mul
import reframe as rfm
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest

class GridBenchmark(SpackTest):
    valid_systems = ['*']
    valid_prog_environs = ['default']
    spack_spec = 'grid@develop'

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = [self.spack_spec]


@rfm.simple_test
class GridBenchmark_ITT(GridBenchmark):
    tags = {"ITT"}
    executable = 'Benchmark_ITT'
    time_limit = '59m'

    mpi = variable(str, value='1.1.1.1')
    shm = variable(int, value=1024)
    num_cpus_per_task = required
    num_tasks_per_node = required

    reference = {
        'cosma8': {
            'Performance': (425000, None, None, 'Mflop/s per node')
        },
        'csd3-icelake': {
            'Performance': (450000, None, None, 'Mflop/s per node')
        },
        'csd3-skylake': {
            'Performance': (22000, None, None, 'Mflop/s per node')
        },
        'dial3': {
            'Performance': (28000, None, None, 'Mflop/s per node')
        },
        'myriad': {
            'Performance': (350000, None, None, 'Mflop/s per node')
        },
        '*': {
            'Performance': (150000, None, None, 'Mflop/s per node'),
        },
    }

    @run_after('setup')
    def setup_num_tasks(self):
        self.num_tasks = reduce(mul, list(map(int, self.mpi.split("."))), 1)
        self.set_var_default(
            'num_cpus_per_task',
            self.current_partition.processor.num_cpus //
            min(1, self.current_partition.processor.num_cpus_per_core))
        self.set_var_default('num_tasks_per_node',
                             self.current_partition.processor.num_cpus //
                             self.num_cpus_per_task)
        self.executable_opts = [f'--mpi {self.mpi}', f'--shm {self.shm}', '--shm-hugetlb']
        self.extra_resources = {
            'mpi': {'num_slots': self.num_tasks * self.num_cpus_per_task}
        }
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'
        self.env_vars['OMP_PLACES'] = 'cores'

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
