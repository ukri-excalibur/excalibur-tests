# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import reframe as rfm
import reframe.utility.sanity as sn
from modules.utils import SpackTest

@rfm.simple_test
class SwiftBenchmark(SpackTest):
    valid_systems = ['*']
    valid_prog_environs = ['default']
    spack_spec = 'swiftsim@0.9.0'
    num_tasks = 4
    num_tasks_per_node = 1
    num_cpus_per_task = 8
    sourcesdir = path.join(path.dirname(__file__), 'input')
    executable = 'swift_mpi'
    time_limit = '20m'
    reference = {
        'cosma8': {
            'duration': (50, None, 0.2, 'seconds'),
        },
        'csd3-skylake': {
            'duration': (50, None, 0.2, 'seconds'),
        },
        'csd3-icelake': {
            'duration': (350, None, 0.2, 'seconds'),
        },
        'dial3': {
            'duration': (150, None, 0.2, 'seconds'),
        },
        'tesseract': {
            'duration': (250, None, 0.2, 'seconds'),
        },
        '*': {
            'duration': (250, None, None, 'seconds'),
        }
    }

    @run_after('setup')
    def setup_variables(self):
        self.executable_opts = ['--hydro', f'--threads={self.num_cpus_per_task}',
                                'sodShock.yml']
        self.extra_resources = {
            'mpi': {'num_slots': self.num_tasks * self.num_cpus_per_task}
        }
        self.variables['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = [self.spack_spec]

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'main: done. Bye.', self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):
        # This performance pattern parses the output of the program to extract
        # the desired figure of merit.
        self.perf_patterns = {
            'duration': sn.extractsingle(
                r'\[(\S+)\] main: done. Bye.',
                self.stdout, 1, float),
        }
