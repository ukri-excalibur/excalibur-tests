# Copyright 2022 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import reframe as rfm
import reframe.utility.sanity as sn

from excalibur_tests.modules.utils import SpackTest

class Cp2kBaseBenchmark(SpackTest):
    valid_systems = ['*']
    valid_prog_environs = ['default']
    spack_spec = 'cp2k@9.1'
    time_limit = '60m'
    num_cpus_per_task = 2
    num_tasks = required
    num_tasks_per_node = required

    @run_after('setup')
    def setup_num_tasks(self):
        self.set_var_default(
            'num_tasks',
            self.current_partition.processor.num_cpus //
            min(1, self.current_partition.processor.num_cpus_per_core) //
            self.num_cpus_per_task)
        self.set_var_default('num_tasks_per_node',
                             self.current_partition.processor.num_cpus //
                             self.num_cpus_per_task)
        self.extra_resources = {
            'mpi': {'num_slots': self.num_tasks * self.num_cpus_per_task}
        }
        self.variables['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'
        self.variables['OMP_PLACES'] = 'cores'
        # For choosing the executable name, see for reference
        # <https://github.com/cp2k/cp2k/blob/e390d0e8443cbafd3d0c65e9488279ca0b9bafcf/benchmarks/QS/check-release-comparison.py#L33>.
        self.executable = f"cp2k.{'p' if self.num_tasks > 0 else 's'}{'smp' if self.num_cpus_per_task > 0 else 'opt'}"

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = [self.spack_spec]

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'T I M I N G', self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):
        self.perf_patterns = {
            'Maximum total time':
            sn.extractsingle(r'CP2K +([0-9]+) +([0-9.]+) +([0-9.]+) +([0-9.]+) +([0-9.]+) +([0-9.]+)', self.stdout, 6, float)
        }


@rfm.simple_test
class Cp2kH2O64Benchmark(Cp2kBaseBenchmark):
    tags = {"h2o-64"}
    sourcesdir = path.join(path.dirname(__file__), 'input-h2o_64')
    executable_opts = ['-i', 'H2O-64.inp']
    reference = {
        'cosma8': {
            'Maximum total time': (25, None, 0.2, 'seconds'),
        },
        'myriad': {
            'Maximum total time': (60, None, 0.2, 'seconds'),
        },
        'tesseract': {
            'Maximum total time': (100, None, 0.2, 'seconds'),
        },
        '*': {
            'Maximum total time': (200, None, None, 'seconds'),
        }
    }


@rfm.simple_test
class Cp2kH2O256Benchmark(Cp2kBaseBenchmark):
    tags = {"h2o-256"}
    sourcesdir = path.join(path.dirname(__file__), 'input-h2o_256')
    executable_opts = ['-i', 'H2O-256.inp']
    reference = {
        'myriad': {
            'Maximum total time': (450, None, 0.2, 'seconds'),
        },
        '*': {
            'Maximum total time': (200, None, None, 'seconds'),
        },
    }


@rfm.simple_test
class Cp2kLiH_HFXBenchmark(Cp2kBaseBenchmark):
    tags = {"lih-hfx"}
    sourcesdir = path.join(path.dirname(__file__), 'input-lih-hfx')
    executable_opts = ['-i', 'input_bulk_B88_3.inp']
    reference = {
        'myriad': {
            'Maximum total time': (225, None, 0.2, 'seconds'),
        },
        'tesseract': {
            'Maximum total time': (400, None, 0.2, 'seconds'),
        },
        '*': {
            'Maximum total time': (200, None, None, 'seconds'),
        }
    }
