# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
import reframe as rfm
import reframe.utility.sanity as sn

from benchmarks.modules.utils import SpackTest

#---------------------------------------------------------
# Shared definitions

input_data_file = 'gromacs_1400k_atoms.tpr'

def get_cpu_executable_opts():
    return ['mdrun', '-noconfout', '-dlb', 'yes', '-s', input_data_file]

def get_gpu_executable_opts():
    return ['mdrun', '-s', input_data_file, '-nb', 'gpu', '-pme', 'gpu', '-bonded', 'gpu', '-dlb', 'no', '-nstlist', '300', '-pin', 'on', '-v', '-gpu_id', '0']

def setup_variables(self):
    """Set the variables required before setup that are common to all tests"""
    # Variables consistent in all tests
    self.exclusive_access = True
    self.executable = 'gmx_mpi_d'
    self.expected_output_file = 'md.log'
    self.keep_files = [self.expected_output_file]
    self.readonly_files = [input_data_file]
    self.reference = {
        '*': {'Rate': (1, None, None, 'ns/day')}
    }
    self.sourcesdir = os.path.dirname(__file__)
    self.time_limit = '45m'

def test_variables(self):
    """Set the variables required after setup, specific to each test"""
    # Test specific variables
    self.num_tasks = self.current_partition.processor.num_cpus * self.num_nodes_param
    self.num_cpus_per_task = 1
    
    self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'
    self.env_vars['OMP_PLACES'] = 'cores'

    if self.current_partition.scheduler.registered_name == 'sge':
        # Set the total number of CPUs to be requested for the SGE scheduler.
        # Set to a full node size to reduce runtime variance.
        self.extra_resources['mpi'] = {'num_slots': self.num_tasks}

def set_sanity_patterns(self):
    """Set the required string in the output for a sanity check"""
    self.sanity_patterns = sn.assert_found(
        'Finished mdrun', self.expected_output_file
    )

def set_perf_patterns(self):
    """Set the regex performance pattern to locate"""
    self.perf_patterns = {
        'Rate': sn.extractsingle('Performance.+', self.expected_output_file, 0,
                                    lambda x: float(x.split()[1]))
    }

#---------------------------------------------------------
# Spack test definitions

class GROMACSSpackBenchmark(SpackTest):
    """Base class for a GROMACS benchmark using the spack build system"""

    valid_systems = ['*']
    valid_prog_environs = ['default']

    spack_spec = 'gromacs@2024 +mpi+double'

    @run_before('setup')
    def setup_spack_setup_variables(self):
        if (self.current_system.name == "kathleen"):
            self.spack_spec += ' ^intel-oneapi-mpi'
        
        setup_variables(self)

    @run_after('setup')
    def setup_spack_test_variables(self):
        test_variables(self)

    @run_before('sanity')
    def set_spack_test_sanity_patterns(self):
        set_sanity_patterns(self)

    @run_before('performance')
    def set_spack_test_perf_patterns(self):
        set_perf_patterns(self)

@rfm.simple_test
class StrongScalingSpackCPUBenchmark(GROMACSSpackBenchmark):
    executable_opts = get_cpu_executable_opts()
    num_nodes_param = parameter([1, 2, 3, 4])


@rfm.simple_test
class StrongScalingSpackGPUBenchmark(GROMACSSpackBenchmark):
    executable_opts = get_gpu_executable_opts()
    num_nodes_param = parameter([1, 2, 3, 4])

#---------------------------------------------------------
# Run-only test definitions

class GROMACSRunOnlyBenchmark(rfm.RunOnlyRegressionTest):
    """Base class for a GROMACS benchmark using a pre-built executable"""

    valid_systems = ['*']
    valid_prog_environs = ['default']

    @run_before('setup')
    def setup_run_only_setup_variables(self):
        setup_variables(self)

    @run_after('setup')
    def setup_run_only_test_variables(self):
        test_variables(self)

    @run_before('sanity')
    def set_run_only_test_sanity_patterns(self):
        set_sanity_patterns(self)

    @run_before('performance')
    def set_run_only_test_perf_patterns(self):
        set_perf_patterns(self)


@rfm.simple_test
class StrongScalingRunOnlyCPUBenchmark(GROMACSRunOnlyBenchmark):
    executable_opts = get_cpu_executable_opts()
    num_nodes_param = parameter([1, 2, 3, 4])


@rfm.simple_test
class StrongScalingRunOnlyGPUBenchmark(GROMACSRunOnlyBenchmark):
    executable_opts = get_gpu_executable_opts()
    num_nodes_param = parameter([1, 2, 3, 4])

#---------------------------------------------------------
