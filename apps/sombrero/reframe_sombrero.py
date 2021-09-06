# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
import os.path as path
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.exceptions import BuildSystemError
from reframe.core.logging import getlogger
from reframe.utility.osext import run_command


@rfm.simple_test
class SombreroBenchmark(rfm.RegressionTest):
    valid_systems = ['*']
    valid_prog_environs = ['*']
    build_system = 'Spack'
    num_tasks = 4
    executable = 'sombrero.sh'
    executable_opts = ['-w', '-s', 'medium', '-n', f'{num_tasks}']
    time_limit = '10m'
    reference = {
        '*': {
            'flops': (30, -0.5, 0.5, 'Gflops/seconds'),
        }
    }
    extra_resources = {
        'mpi': {'num_slots': num_tasks}
    }

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = ['sombrero@2021-07-08']
        # Select the Spack environment:
        # * if `EXCALIBUR_SPACK_ENV` is set, use that one
        # * if not, use a provided spack environment for the current system
        # * if that doesn't exist, create a persistent minimal environment
        # TODO: this snippet should be in a utility function that all tests will
        # use
        if os.getenv('EXCALIBUR_SPACK_ENV'):
            self.build_system.environment = os.getenv('EXCALIBUR_SPACK_ENV')
        else:
            env = path.realpath(
                path.join(path.dirname(__file__), '..', '..', 'spack-environments',
                          self.current_system.name)
            )
            if not path.isdir(env):
                cmd = run_command(["spack", "env", "create", "-d", env])
                if cmd.returncode != 0:
                    raise BuildSystemError("Creation of the Spack "
                                           f"environment {env} failed")
                cmd = run_command(["spack", "-e", env, "config", "add",
                                   "config:install_tree:root:opt/spack"])
                if cmd.returncode != 0:
                    raise BuildSystemError("Setting up the Spack "
                                           f"environment {env} failed")
                getlogger().info("Spack environment successfully created at"
                                 f"{env}")

            self.build_system.environment = env

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'\[RESULT\] SUM', self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):
        self.perf_patterns = {
            'flops': sn.extractsingle(r'\[RESULT\] SUM (\S+) Gflops/seconds',
                                      self.stdout, 1, float),
        }
