# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os.path as path
import sys
import reframe as rfm
import reframe.utility.sanity as sn

sys.path.append(path.join(path.dirname(__file__), '..', '..'))
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
    executable_opts = ['--hydro', f'--threads={num_cpus_per_task}',
                       'sodShock.yml']
    time_limit = '20m'
    variables = {
        'OMP_NUM_THREADS': f'{num_cpus_per_task}',
    }
    extra_resources = {
        'mpi': {'num_slots': num_tasks * num_cpus_per_task}
    }
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
