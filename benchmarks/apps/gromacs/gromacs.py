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

def get_cpu_executable_opts():
    return ['mdrun', '-noconfout', '-dlb', 'yes', '-s', 'gromacs_1400k_atoms.tpr']

def get_gpu_executable_opts():
    return ['mdrun', '-s', 'gromacs_1400k_atoms.tpr', '-nb', 'gpu', '-pme', 'gpu', '-bonded', 'gpu', '-dlb', 'no', '-nstlist', '300', '-pin', 'on', '-v', '-gpu_id', '0']

def setup_variables(self):
    """Set the variables common to all tests"""
    # Variables consistent in all tests
    self.exclusive_access = True
    self.executable = 'gmx_mpi'
    self.expected_output_file = 'md.log'
    self.keep_files = [self.expected_output_file]
    self.readonly_files = ['gromacs_1400k_atoms.tpr']
    self.reference = {
        '*': {'Rate': (1, None, None, 'ns/day')}
    }
    self.sourcesdir = os.path.dirname(__file__)
    self.time_limit = '240m'
    self.valid_prog_environs = ['default']
    self.valid_systems = ['*']

    # Test specific variables
    self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'
    self.env_vars['OMP_PLACES'] = 'cores'
    self.num_cpus_per_task = 1
    self.num_tasks = self.current_partition.processor.num_cpus * self.num_nodes_param
    self.outputdir = self.dir_prefix + str(self.num_nodes_param)

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

    spack_spec = 'gromacs@2024 +mpi +double'

    @run_after('setup')
    def setup_spack_testvariables(self):
        setup_variables(self)

    @run_before('sanity')
    def set_spack_test_sanity_patterns(self):
        set_sanity_patterns(self)

    @run_before('performance')
    def set_spack_test_perf_patterns(self):
        set_perf_patterns(self)

@rfm.simple_test
class StrongScalingSpackCPUBenchmark(GROMACSSpackBenchmark):
    dir_prefix = 'StrongScalingCPUBenchmark_'
    executable_opts = get_cpu_executable_opts()
    num_nodes_param = parameter([1, 2, 3, 4])


@rfm.simple_test
class StrongScalingSpackGPUBenchmark(GROMACSSpackBenchmark):
    dir_prefix = 'StrongScalingGPUBenchmark_'
    executable_opts = get_gpu_executable_opts()
    num_nodes_param = parameter([1, 2, 3, 4])

#---------------------------------------------------------
# Run-only test definitions

class GROMACSRunOnlyBenchmark(rfm.RunOnlyRegressionTest):
    """Base class for a GROMACS benchmark using a pre-built executable"""

    @run_after('setup')
    def setup_spack_testvariables(self):
        setup_variables(self)

    @run_before('sanity')
    def set_spack_test_sanity_patterns(self):
        set_sanity_patterns(self)

    @run_before('performance')
    def set_spack_test_perf_patterns(self):
        set_perf_patterns(self)


@rfm.simple_test
class StrongScalingRunOnlyCPUBenchmark(GROMACSRunOnlyBenchmark):
    dir_prefix = 'StrongScalingRunOnlyCPUBenchmark_'
    executable_opts = get_cpu_executable_opts()
    num_nodes_param = parameter([1, 2, 3, 4])


@rfm.simple_test
class StrongScalingRunOnlyGPUBenchmark(GROMACSRunOnlyBenchmark):
    dir_prefix = 'StrongScalingRunOnlyGPUBenchmark_'
    executable_opts = get_gpu_executable_opts()
    num_nodes_param = parameter([1, 2, 3, 4])

#---------------------------------------------------------
