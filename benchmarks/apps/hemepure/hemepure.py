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
    readonly_files = [
        input_data_file,
        'ArteryTriangleSet.stl',
        'hemepure.py',
        'pipe.gmy',
        'pipe.stl',
        'pipe.xml'
    ]
    sourcesdir = os.path.dirname(__file__)
    
    reference = {
        '*': {
            'Timestep': (100, None, None, 's'),
        }
    }
        
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

    # @run_before('sanity')
    # def set_test_sanity_patterns(self):
    #     """Set the required string in the output for a sanity check"""

    @run_before('performance')
    def set_test_perf_patterns(self):
        """Set the regex performance pattern to locate"""
        self.perf_patterns = {
            'Timestep': sn.extractsingle(r'\[Rank \d+, \S+ s, \d+ kB] :: time step 0*(?P<timestep>\d+)(\s+\S+)+',
                                     self.expected_output_file, 'timestep', float, item=-1)
        }

@rfm.simple_test
class StrongScalingCPU(HemepureBenchmark):
    spack_spec = "hemepure +pressure_bc"
    num_nodes_param = parameter([1, 2, 3, 4])
    
    output_file_prefix = 'PipeCPU_PBC'

    executable = 'hemepure'
