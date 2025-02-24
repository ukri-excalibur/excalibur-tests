# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.decorators import run_before, run_after

from benchmarks.modules.utils import SpackTest

class GROMACSBenchmark(SpackTest):
    """Base class for a GROMACS benchmark"""

    valid_systems = ['*']
    valid_prog_environs = ['default']
    spack_spec = 'gromacs@2019' 
    executable = 'gmx_mpi'
    executable_opt = ['mdrun', '-noconfout', '-dlb', 'yes', '-s', 'gromacs_1400k_atoms.tpr']
    time_limit = '60m'
    exclusive_access = True

    sourcesdir = os.path.dirname(__file__)
    readonly_files = ['gromacs_1400k_atoms.tpr']

    reference = {
        '*': {'Rate': (1, None, None, 'ns/day')}
    }

    num_nodes = 4
    num_tasks = 128
    num_cpus_per_task = 1

    @run_after('setup')
    def setup_variables(self):
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'
        self.env_vars['OMP_PLACES'] = 'cores'

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

    variant = parameter([4 * i for i in range(1, 6)])
    num_omp_threads = 4

    @run_before('setup')
    def set_total_num_cores(self):
        """A ReFrame parameter cannot also be a variable, thus assign
        them to be equal at the start of the setup"""
        self.num_total_cores = self.variant
