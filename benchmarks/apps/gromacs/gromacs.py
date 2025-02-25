# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
import reframe as rfm
import reframe.utility.sanity as sn

from benchmarks.modules.utils import SpackTest

class GROMACSBenchmark(SpackTest):
    """Base class for a GROMACS benchmark"""

    valid_systems = ['*']
    valid_prog_environs = ['default']
    spack_spec = 'gromacs@2019' 
    executable = 'gmx_mpi'
    executable_opt = ['mdrun', '-noconfout', '-dlb', 'yes', '-s', 'gromacs_1400k_atoms.tpr']
    time_limit = '120m'
    exclusive_access = True

    sourcesdir = os.path.dirname(__file__)
    readonly_files = ['gromacs_1400k_atoms.tpr']

    reference = {
        '*': {'Rate': (1, None, None, 'ns/day')}
    }

    @run_after('setup')
    def setup_variables(self):
        self.num_nodes = 4
        self.num_tasks = self.num_tasks_param
        self.num_cpus_per_task = self.num_cpus_per_task_param
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'
        self.env_vars['OMP_PLACES'] = 'cores'

        if self.current_partition.scheduler.registered_name == 'sge':
            # Set the total number of CPUs to be requested for the SGE scheduler.
            # Set to a full node size to reduce runtime variance.
            self.extra_resources['mpi'] = {'num_slots': self.current_partition.processor.num_cpus}

    @run_before('sanity')
    def set_sanity_patterns(self):
        """Set the required string in the output for a sanity check"""
        self.sanity_patterns = sn.assert_found(
            'GROMACS reminds you', self.stderr
        )

    @run_before('performance')
    def set_perf_patterns(self):
        """Set the regex performance pattern to locate"""
        self.perf_patterns = {
            'Rate': sn.extractsingle('Performance.+', self.stderr, 0,
                                     lambda x: float(x.split()[1]))
        }


@rfm.simple_test
class StrongScalingBenchmark(GROMACSBenchmark):
    num_tasks_param = parameter([4 * i for i in range(1, 6)])
    num_cpus_per_task_param = 4


@rfm.simple_test
class ThreadAndRankVariationTest(GROMACSBenchmark):
    num_tasks_param = parameter([2,4,8,16,32])
    num_cpus_per_task_param = parameter([1,2,4,8])
    num_omp_threads = 4
