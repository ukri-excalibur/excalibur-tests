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
    time_limit = '240m'
    exclusive_access = True

    sourcesdir = os.path.dirname(__file__)
    readonly_files = ['gromacs_1400k_atoms.tpr']

    reference = {
        '*': {'Rate': (1, None, None, 'ns/day')}
    }

    expected_output_file = 'md.log'

    @run_after('setup')
    def setup_variables(self):
        self.num_tasks = self.current_partition.processor.num_cpus * self.num_nodes_param
        self.num_cpus_per_task = 1
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'
        self.env_vars['OMP_PLACES'] = 'cores'

        if self.current_partition.scheduler.registered_name == 'sge':
            # Set the total number of CPUs to be requested for the SGE scheduler.
            # Set to a full node size to reduce runtime variance.
            self.extra_resources['mpi'] = {'num_slots': self.num_tasks}

    @run_before('sanity')
    def set_sanity_patterns(self):
        """Set the required string in the output for a sanity check"""
        self.sanity_patterns = sn.assert_found(
            'Finished mdrun', self.expected_output_file
        )

    @run_before('performance')
    def set_perf_patterns(self):
        """Set the regex performance pattern to locate"""
        self.perf_patterns = {
            'Rate': sn.extractsingle('Performance.+', self.expected_output_file, 0,
                                     lambda x: float(x.split()[1]))
        }

@rfm.simple_test
class StrongScalingCPUBenchmark(GROMACSBenchmark):
    num_nodes_param = parameter([1, 2, 3, 4])
    executable_opts = ['mdrun', '-noconfout', '-dlb', 'yes', '-s', 'gromacs_1400k_atoms.tpr']


@rfm.simple_test
class StrongScalingGPUBenchmark(GROMACSBenchmark):
    num_nodes_param = parameter([1, 2, 3, 4])
    executable_opts = ['mdrun', '-s', 'gromacs_1400k_atoms.tpr', '-nb', 'gpu', '-pme', 'gpu', '-bonded', 'gpu', '-dlb', 'no', '-nstlist', '300', '-pin', 'on', '-v', '-gpu_id', '0']

