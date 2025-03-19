# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
import reframe as rfm
import reframe.utility.sanity as sn

from benchmarks.modules.utils import SpackTest


input_data_file = 'input.xml'

class HemepureBenchmark(SpackTest):
    """Base class for a Hemepure benchmark using the spack build system"""

    valid_systems = ['*']
    valid_prog_environs = ['default']

    # Variables consistent in all tests
    exclusive_access = True
    time_limit = '45m'

    expected_output_file = 'md.log'
    readonly_files = [input_data_file]
    sourcesdir = os.path.dirname(__file__)
    
    energy_ref = -1206540.0
    reference = {}
        
    @run_after('setup')
    def setup_spack_test_variables(self):
        """Set the variables required after setup, specific to each test"""
        # Test specific variables
        self.num_tasks = self.current_partition.processor.num_cpus * self.num_nodes_param
        self.num_cpus_per_task = 1
        
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'
        self.env_vars['OMP_PLACES'] = 'cores'

        self.keep_files = [self.output_file_prefix + '_NN' + str(self.num_nodes_param) + '_NP' + str(self.num_tasks)]
        self.executable_opts = ['-in', input_data_file, '-out', self.keep_files[0]]

    @run_before('sanity')
    def set_test_sanity_patterns(self):
        """Set the required string in the output for a sanity check"""

    @run_before('performance')
    def set_test_perf_patterns(self):
        """Set the regex performance pattern to locate"""

@rfm.simple_test
class StrongScalingCPU(HemepureBenchmark):
    spack_spec = "hemepure +pressure_bc"
    num_nodes_param = parameter([4])#1, 2, 4, 8])
    
    output_file_prefix = 'PipeCPU_PBC'

    executable = 'hemepure'
