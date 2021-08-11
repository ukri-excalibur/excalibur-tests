# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
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
                path.join(path.dirname(__file__), '..', '..', 'spack-environments',
                          self.current_system.name)
            )
            if path.isdir(env):
                self.build_system.environment = env
            else:
                self.build_system.environment = None

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'\[RESULT\] SUM', self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):
        self.perf_patterns = {
            'flops': sn.extractsingle(r'\[RESULT\] SUM (\S+) Gflops/seconds',
                                      self.stdout, 1, float),
        }
