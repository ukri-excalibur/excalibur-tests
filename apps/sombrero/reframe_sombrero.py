# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import reframe as rfm
import reframe.utility.sanity as sn
from modules.reframe_extras import scaling_config


@rfm.simple_test
class SombreroBenchmark(rfm.RegressionTest):
    def __init__(self):
        self.valid_systems = ['*']
        self.valid_prog_environs = ['*']
        self.build_system = 'Spack'
        self.executable = 'sombrero.sh'
        self.num_tasks = 2
        self.time_limit = '10m'
        self.reference = {
            '*': {
                'flops_average': (0, None, None, 'Gflops/seconds'),
                'flops_1': (0, None, None, 'Gflops/seconds'),
                'flops_2': (0, None, None, 'Gflops/seconds'),
                'flops_3': (0, None, None, 'Gflops/seconds'),
                'flops_4': (0, None, None, 'Gflops/seconds'),
                'flops_5': (0, None, None, 'Gflops/seconds'),
                'flops_6': (0, None, None, 'Gflops/seconds'),
            }
        }

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.environment = '.'
        self.build_system.specs = ['sombrero@2021-07-31']

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.all(
            [sn.assert_found(r'\[RESULT\] SUM', self.stdout)] + [
                sn.assert_found(r'\[RESULT\]\[0]\ Case '
                                f'{i}', self.stdout) for i in range(1, 7)
            ])

    @run_before('performance')
    def set_perf_patterns(self):

        pattern_template = r'\[RESULT\]\[0\] Case {i} (\S+) Gflops/seconds'

        pattern_dict = [(f"flops_{i}", pattern_template.format(i=i))
                        for i in range(1, 7)]
        pattern_dict.append(
            ('flops_average', r'\[RESULT\] SUM (\S+) Gflops/seconds'))

        self.perf_patterns = dict(
            (pattern[0], sn.extractsingle(pattern[1], self.stdout, 1, float))
            for pattern in pattern_dict)

        print(self.perf_patterns)


@rfm.parameterized_test(*scaling_config())
class SombreroBenchmarkStrongMedium(SombreroBenchmark):
    def __init__(self, part, num_tasks, num_tasks_per_node):
        self.executable_opts = ['-n', f"{num_tasks}", "medium"]


@rfm.parameterized_test(*scaling_config())
class SombreroBenchmarkWeakMedium(SombreroBenchmark):
    def __init__(self, part, num_tasks, num_tasks_per_node):
        self.executable_opts = ['-n', f"{num_tasks}", "-w", "medium"]
