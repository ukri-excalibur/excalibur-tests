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

from modules.reframe_extras import scaling_config

from apps.sombrero import case_filter

@rfm.simple_test
class SombreroBenchmarkScaling(rfm.RegressionTest):
    params = parameter(case_filter.generate(scaling_config))

    def __init__(self):
        self.valid_systems = ['*']
        self.valid_prog_environs = ['*']
        self.build_system = 'Spack'
        self.time_limit = '10m'

        self.reference = {
            '*': {
                'flops': (0, None, None, 'Gflops/second'),
                'time': (10, None, None, 'second'),
                'communicated': (0, None, None, 'byte'),
                'avg_arithmetic_intensity': (0, None, None, 'Flops/byte'),
                'computation/communication': (0, None, None, 'Flops/byte'),
            }
        }

    @run_after('init')
    def set_up_from_parameters(self):
        self.theory_str = str(self.params[case_filter.Idx.theory_id])
        self.executable = 'sombrero' + self.theory_str
        self.executable_opts = []
        if self.params[case_filter.Idx.strong_or_weak] == "weak":
            self.executable_opts.append('-w')
        self.executable_opts += ['-s', self.params[case_filter.Idx.size]]
        self.num_tasks = self.params[case_filter.Idx.nprocesses]
        self.extra_resources = { # TODO: check that this can be an instance variable
            'mpi': {'num_slots': self.num_tasks}
        }

    @run_before('compile')
    def setup_build_system(self):
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

        self.build_system.specs = ['sombrero@2021-07-31']

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(
            r'\[RESULT\]\[0]\ Case ' + self.theory_str, self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):

        self.perf_patterns = {
            'flops':
            sn.extractsingle(r'\[RESULT\]\[0\] Case ' +
                             self.theory_str +
                             r' (\S+) Gflops/seconds', 1, self.stdout),
            'time':sn.extractsingle(r'\[RESULT\]\[0\] Case ' +
                             self.theory_str +
                             r' \S+ Gflops in (\S+) seconds', 1, self.stdout),
            'communicated': sn.extractsingle(r'\[MAIN\]\[0\] Case ' +
                             self.theory_str +
                             r' .* (\S+) bytes communicated', 1, self.stdout),
            'avg_arithmetic_intensity': sn.extractsingle(r'\[MAIN\]\[0\] Case ' +
                             self.theory_str +
                             r' (\S+) average arithmetic intensity', 1, self.stdout),
            'computation/communication': sn.extractsingle(r'\[MAIN\]\[0\] Case ' +
                             self.theory_str +
                             r' (\S+) flop per byte communicated', 1, self.stdout),
        }
