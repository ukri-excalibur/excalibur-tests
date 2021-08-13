# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
import os.path as path
import reframe as rfm
import reframe.utility.sanity as sn
from modules.reframe_extras import scaling_config
import itertools as it
from enum import IntEnum


class SombreroCase:
    class Idx(IntEnum):
        # See _flatten_nested_case() and generate()
        strong_or_weak = 0
        size = 1
        partition = 2
        nprocesses = 3
        nprocesses_per_node = 4
        theory_id = 5

    @staticmethod
    def _flatten_nested_case(nested_case):
        # See Idx and generate()
        return (
            nested_case[0],  # strong/weak
            nested_case[1],  # size
            *nested_case[2],  # input from scaling config
            nested_case[3])  # theory_id

    @staticmethod
    def _check_nprocesses(np):
        '''
        Make sure the number of processes is 2^n or 2^n x 3
        '''
        assert np > 0
        if np % 2 == 1:
            return np in [1, 3]
        else:
            return SombreroCase._check_nprocesses(np // 2)

    @staticmethod
    def _case_filter(case):
        strong_or_weak = case[SombreroCase.Idx.strong_or_weak]
        size = case[SombreroCase.Idx.size]
        nprocesses = case[SombreroCase.Idx.nprocesses]

        if not SombreroCase._check_nprocesses(nprocesses):
            return False
        if strong_or_weak == "weak" and size != "medium":
            return False

        return True

    @staticmethod
    def generate(scaling_config):
        theory_ids = range(1, 7)
        sizes = ['small', 'medium', 'large', 'very_large']
        strong_or_weak = ['strong', 'weak']

        # See Idx and _flatten_nested_case()
        nested_cases = it.product(strong_or_weak, sizes, scaling_config(),
                                  theory_ids)

        cases = map(SombreroCase._flatten_nested_case, nested_cases)

        filtered = filter(SombreroCase._case_filter, cases)

        filtered_list = list(filtered)
        for case in filtered_list:
            assert len(case) == 6
        return filtered_list


@rfm.simple_test
class SombreroBenchmark(rfm.RegressionTest):
    params = parameter(SombreroCase.generate(scaling_config))

    def __init__(self):
        self.valid_systems = ['*']
        self.valid_prog_environs = ['*']
        self.build_system = 'Spack'
        self.time_limit = '10m'

        self.reference = {
            '*': {
                'flops': (0, None, None, 'Gflops/seconds'),
            }
        }

    @run_after('init')
    def set_up_from_parameters(self):
        self.theory_str = str(self.params[SombreroCase.Idx.theory_id])
        self.executable = 'sombrero' + self.theory_str
        self.executable_opts = []
        if self.params[SombreroCase.Idx.strong_or_weak] == "weak":
            self.executable_opts.append('-w')
        self.executable_opts += ['-s', self.params[SombreroCase.Idx.size]]
        self.num_tasks = self.params[SombreroCase.Idx.nprocesses]

    @run_before('compile')
    def setup_build_system(self):
        # Select the Spack environment:
        # * if `EXCALIBUR_SPACK_ENV` is set, use that one
        # * if not, use a provided spack environment for the current system
        # * if that doesn't exist, default to `None` and let ReFrame
        #   automatically create a minimal environment
        # TODO: this snippet should be in a utility function that all tests will
        # use
        if os.getenv('EXCALIBUR_SPACK_ENV'):
            self.build_system.environment = os.getenv('EXCALIBUR_SPACK_ENV')
        else:
            env = path.realpath(
                path.join(path.dirname(__file__), '..', '..',
                          'spack-environments', self.current_system.name))
            if path.isdir(env):
                self.build_system.environment = env
            else:
                self.build_system.environment = None

        self.build_system.specs = ['sombrero@2021-07-31']

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(
            r'\[RESULT\]\[0]\ Case ' + self.theory_str, self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):

        pattern_template = r'\[RESULT\]\[0\] Case {i} (\S+) Gflops/seconds'

        self.perf_patterns = {
            'flops':
            sn.extractsingle(r'\[RESULT\]\[0\] Case ' + self.theory_str + r' (\S+) Gflops/seconds', 1, self.stdout
            )
        }
