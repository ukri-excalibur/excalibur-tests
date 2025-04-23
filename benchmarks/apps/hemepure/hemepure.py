# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
import reframe as rfm
import reframe.utility.sanity as sn

from benchmarks.modules.utils import SpackTest

input_data = 'input_data/pipe'

class HemepureBenchmark(SpackTest):
    """Base class for a Hemepure benchmark using the spack build system"""

    valid_systems = ['*']
    valid_prog_environs = ['default']

    # Variables consistent in all tests
    time_limit = '45m'

    # expected_output_file = 'md.log'
    readonly_files = [input_data]
    sourcesdir = os.path.dirname(__file__)
    
    reference = {
        '*': {
            'Runtime': (160.0, None, None, 'MLUPS'),
        }
    }
        
    @run_after('setup')
    def setup_test_variables(self):
        """Set the variables required after setup, specific to each test"""
        self.num_tasks_per_node = int(self.current_partition.processor.num_cpus / self.current_partition.processor.num_cpus_per_core)
        self.num_tasks = self.num_tasks_per_node * self.num_nodes_param
        self.num_nodes = self.num_nodes_param
        self.num_cpus_per_task = 1

        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'
        self.env_vars['OMP_PLACES'] = 'cores'

        self.output_dir = self.output_file_prefix + '_NN' + str(self.num_nodes_param) + '_NP' + str(self.num_tasks)
        self.keep_files = [self.output_dir]
        self.executable_opts = ['-in', input_data + '/input.xml', '-out', self.keep_files[0]]

    @run_before('sanity')
    def set_test_sanity_patterns(self):
        """Set the required string in the output for a sanity check"""
        self.sanity_patterns = sn.assert_found(
            'SIMULATION FINISHED', self.stdout
        )

    @run_before('performance')
    def set_test_perf_patterns(self):
        """Set the regex performance pattern to locate"""
        runtime = sn.extractsingle(r'\[Rank \d+, (?P<runtime>\S+) s, \d+ kB] :: SIMULATION FINISHED',
            self.stdout, 'runtime', float, item=-1)

        output_file = self.output_dir + "/report.xml"
        timesteps = sn.extractsingle(r'\<steps\>(?P<timesteps>\S+)\<\/steps\>',
            output_file, 'runtime', float, item=-1)

        sites = sn.extractsingle(r'\<sites\>(?P<sites>\S+)\<\/sites\>',
            output_file, 'sites', float, item=-1)

        self.perf_patterns = {
            'Performance': (sites * timesteps) / (1e6 * runtime)
        }

@rfm.simple_test
class StrongScalingPipeCPU(HemepureBenchmark):
    valid_systems = ['-gpu']
    spack_spec = "hemepure +pressure_bc"
    executable = 'hemepure'
    output_file_prefix = 'PipeCPU_PBC'
    
    num_nodes_param = parameter([1, 2, 3, 4])

# This test is incomplete and thus has been disabled 
# until future work can complete it.
# @rfm.simple_test
# class StrongScalingPipeGPU(HemepureBenchmark):
#     valid_systems = ['+gpu +cuda']
#     spack_spec = "hemepure-gpu +pressure_bc"
#     executable = 'hemepure_gpu'
#     output_file_prefix = 'PipeGPU_PBC'
    
#     num_nodes_param = parameter([2, 4, 8, 16])
#     num_gpus_per_node_param = parameter([1, 2, 4])
    
#     @run_before('compile')
#     def set_num_tasks(self):
#         self.extra_resources['gpu'] = {'num_gpus_per_node': self.num_gpus_per_node_param}
