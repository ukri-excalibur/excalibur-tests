# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
import reframe as rfm
import reframe.utility.sanity as sn

from benchmarks.modules.utils import SpackTest


input_data_file = 'gromacs_1400k_atoms.tpr'

class GROMACSBenchmark(SpackTest):
    """Base class for a GROMACS benchmark using the spack build system"""

    valid_systems = ['*']
    valid_prog_environs = ['default']

    # Variables consistent in all tests
    exclusive_access = True
    time_limit = '45m'

    expected_output_file = 'md.log'
    keep_files = [expected_output_file]
    readonly_files = [input_data_file]
    sourcesdir = os.path.dirname(__file__)
    executable = 'gmx_mpi'
    
    reference = {
        'kathleen:compute-node': {
            'Rate': (1, -0.1, None, 'ns/day'),
            'Energy': (-12070100.0, -1.0, 1.0, 'kJ/mol')
        },
        '*': {
            'Rate': (1, None, None, 'ns/day'),
            'Energy': (1, None, None, 'kJ/mol')
        }
    }
        
    @run_after('setup')
    def setup_test_variables(self):
        """Set the variables required after setup, specific to each test"""
        # Test specific variables
        self.num_tasks = self.current_partition.processor.num_cpus * self.num_nodes_param
        self.num_cpus_per_task = 1
        
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'
        self.env_vars['OMP_PLACES'] = 'cores'

    @run_before('sanity')
    def set_test_sanity_patterns(self):
        """Set the required string in the output for a sanity check"""
        self.sanity_patterns = sn.assert_found(
            'Finished mdrun', self.expected_output_file
        )

    @run_before('performance')
    def set_test_perf_patterns(self):
        """Set the regex performance pattern to locate"""
        self.perf_patterns = {
            'Rate': sn.extractsingle(r'Performance:\s+(?P<rate>\S+)(\s+\S+){1}',
                                     self.expected_output_file, 'rate', float),
            'Energy': sn.extractsingle(r'\s+Potential\s+Kinetic En\.\s+Total Energy\s+Conserved En\.\s+Temperature\n'
                                       r'(\s+\S+){2}\s+(?P<energy>\S+)(\s+\S+){2}\n'
                                       r'\s+Pressure \(bar\)\s+Constr\. rmsd',
                                       self.expected_output_file, 'energy', float),
        }

@rfm.simple_test
class StrongScalingCPU(GROMACSBenchmark):
    spack_spec = 'gromacs@2024 +mpi'

    executable_opts = ['mdrun', '-noconfout', '-dlb', 'yes', '-s', input_data_file]
    num_nodes_param = parameter([1, 2, 3, 4])


@rfm.simple_test
class StrongScalingSpackGPU(GROMACSBenchmark):
    spack_spec = 'gromacs@2024 +mpi+cuda'

    executable_opts = ['mdrun', '-s', input_data_file, '-nb', 'gpu', '-pme', 'gpu', '-bonded', 'gpu', '-dlb', 'no', '-nstlist', '300', '-pin', 'on', '-v', '-gpu_id', '0']
    num_nodes_param = parameter([1, 2, 3, 4])
