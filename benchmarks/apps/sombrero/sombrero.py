# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import reframe as rfm
import reframe.utility.sanity as sn

from benchmarks.apps.sombrero import case_filter
from benchmarks.modules.reframe_extras import scaling_config
from benchmarks.modules.utils import SpackTest

# Fixed lattice volume in ITT benchmarks
LATTICE_VOLUME_SMALL = 32 * 24 ** 3
LATTICE_VOLUME_MEDIUM = 48 ** 3 * 64


# Helper function to find maximum number of tasks we can use for benchmarks
# which assume the number of cores divide a fixed lattice volume.
def max_num_tasks(n, volume):
    num_tasks = 1
    for i in range(2, n + 1):
        if volume % i == 0:
            num_tasks = i
    return num_tasks


@rfm.simple_test
class SombreroBenchmarkBase(SpackTest):
    valid_systems = ['-gpu']
    valid_prog_environs = ['default']
    time_limit = '3m'
    spack_spec = 'sombrero@2021-08-16'
    theory_id = parameter(range(1, 7))

    @run_after('init')
    def set_executable(self):
        self.executable = f"sombrero{self.theory_id}"

    @run_after('init')
    def set_references(self):
        i = self.theory_id
        reference = {
            '*': {
                f'flops{i}': (0, None, None, 'Gflops/second'),
                f'time{i}': (10, None, None, 'second'),
                f'communicated{i}': (0, None, None, 'byte'),
                f'avg_arithmetic_intensity{i}': (0, None, None, 'Flops/byte'),
                f'computation/communication{i}': (0, None, None, 'Flops/byte'),
            }
        }

    @run_before('sanity')
    def set_sanity_patterns(self):
        i = self.theory_id
        self.sanity_patterns = sn.assert_found(
            r'\[RESULT\]\[0]\ Case ' + str(i), self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):
        i = self.theory_id
        self.perf_patterns = {
            f'flops{i}':
            sn.extractsingle(
                r'\[RESULT\]\[0\] Case ' + str(i) + r' (\S+) Gflops/seconds',
                self.stdout, 1, float),
            f'time{i}':
            sn.extractsingle(
                r'\[RESULT\]\[0\] Case ' + str(i) +
                r' \S+ Gflops in (\S+) seconds', self.stdout, 1, float),
            f'communicated{i}':
            sn.extractsingle(
                r'\[MAIN\]\[0\] Case ' + str(i) +
                r': .* (\S+) bytes communicated', self.stdout, 1, float),
            f'avg_arithmetic_intensity{i}':
            sn.extractsingle(
                r'\[MAIN\]\[0\] Case ' + str(i) +
                r': (\S+) average arithmetic intensity', self.stdout, 1,
                float),
            f'computation/communication{i}':
            sn.extractsingle(
                r'\[MAIN\]\[0\] Case ' + str(i) +
                r': (\S+) flop per byte communicated', self.stdout, 1, float),
        }


@rfm.simple_test
class SombreroBenchmarkMini(SombreroBenchmarkBase):
    valid_systems = ['-gpu']
    tags = {"mini"}

    @run_after('init')
    def set_up_from_parameters(self):
        self.executable_opts = ['-l', '8x4x4x4', '-p', '2x1x1x1']
        self.num_tasks = 2


@rfm.simple_test
class SombreroBenchmarkScaling(SombreroBenchmarkBase):
    params = parameter(case_filter.generate(scaling_config))
    valid_systems = ['-gpu']
    tags = {"scaling"}

    @run_after('init')
    def set_up_from_parameters(self):
        self.executable_opts = []
        if self.params[case_filter.Idx.strong_or_weak] == "weak":
            self.executable_opts.append('-w')
        self.executable_opts += ['-s', self.params[case_filter.Idx.size]]
        self.num_tasks = self.params[case_filter.Idx.nprocesses]


@rfm.simple_test
class SombreroITTsn(SombreroBenchmarkBase):
    valid_systems = ['-gpu']
    tags = {"ITT-sn"}

    @run_after('init')
    def set_up_from_parameters(self):
        self.executable_opts = ['-s', 'small']

    @run_after('setup')
    def setup_num_tasks(self):
        self.num_tasks = max_num_tasks(
            self.current_partition.processor.num_cores,
            LATTICE_VOLUME_SMALL,
        )

@rfm.simple_test
class SombreroITT64n(SombreroBenchmarkBase):
    valid_systems = ['-gpu']
    tags = {"ITT-64n"}

    @run_after('init')
    def set_up_from_parameters(self):
        self.executable_opts = ['-s', 'medium']

    @run_after('setup')
    def setup_num_tasks(self):
        self.num_tasks_per_node = max_num_tasks(
            self.current_partition.processor.num_cores,
            LATTICE_VOLUME_MEDIUM // 64,
        )
        self.num_tasks = self.num_tasks_per_node * 64
