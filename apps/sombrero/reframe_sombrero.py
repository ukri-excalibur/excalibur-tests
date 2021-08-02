# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os.path as path
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class SombreroBenchmark(rfm.RegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['*']
    build_system = 'Spack'
    executable = 'sombrero.sh'
    executable_opts = ['-w', '-s', 'medium', '-n', '4']
    time_limit = '10m'
    reference = {
        '*': {
            'flops': (30, -0.5, 0.5, 'Gflops/seconds'),
        }
    }

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = ['sombrero@2021-07-08']
        self.build_system.environment = path.realpath(
            path.join(path.dirname(__file__), '..', '..', 'spack-environments',
                      self.current_system.name)
        )

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'\[RESULT\] SUM', self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):
        self.perf_patterns = {
            'flops': sn.extractsingle(r'\[RESULT\] SUM (\S+) Gflops/seconds',
                                      self.stdout, 1, float),
        }
