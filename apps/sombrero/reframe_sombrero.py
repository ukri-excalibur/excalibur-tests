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
import reframe.utility.udeps as udeps

from modules.reframe_extras import scaling_config

from apps.sombrero import case_filter



def identify_build_environment(current_system_name):
    if os.getenv('EXCALIBUR_SPACK_ENV'):
        env = os.getenv('EXCALIBUR_SPACK_ENV')
    else:
        env = path.realpath(
            path.join(path.dirname(__file__), '..', '..',
                      'spack-environments', current_system_name))
        if not path.isdir(env):
            cmd = run_command(["spack", "env", "create", "-d", env])
            if cmd.returncode != 0:
                raise BuildSystemError("Creation of the Spack "
                                       f"environment {env} failed")
            cmd = run_command([
                "spack", "-e", env, "config", "add",
                "config:install_tree:root:opt/spack"
            ])
            if cmd.returncode != 0:
                raise BuildSystemError("Setting up the Spack "
                                       f"environment {env} failed")
            getlogger().info("Spack environment successfully created at"
                             f"{env}")
    return env



@rfm.simple_test
class SombreroBuild(rfm.CompileOnlyRegressionTest):
    descr = "Build SOMBRERO"
    valid_systems = ['*']
    valid_prog_environs = ['*']
    build_system = 'Spack'

    @run_before('compile')
    def setup_build_system(self):
        # Select the Spack environment:
        # * if `EXCALIBUR_SPACK_ENV` is set, use that one
        # * if not, use a provided spack environment for the current system
        # * if that doesn't exist, create a persistent minimal environment
        # TODO: this snippet should be in a utility function that all tests will
        # use
        self.build_system.environment = identify_build_environment(self.current_system.name)
        self.build_system.specs = ['sombrero@2021-08-16']

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_not_found("error", self.stderr)


@rfm.simple_test
class SombreroBenchmarkBase(rfm.RegressionTest):
    valid_systems = []
    valid_prog_environs = ['*']
    build_system = 'Spack'
    time_limit = '3m'
    theory_id = parameter(range(1,7))

    @run_after('init')
    def inject_dependencies(self):
        self.depends_on("SombreroBuild", udeps.fully)
        self.build_system.environment = identify_build_environment(self.current_system.name)
        self.build_system.specs = ['sombrero@2021-08-16']

    @run_after('init')
    def set_executable(self):
        self.executable = f"sombrero{self.theory_id}"

    @run_after('init')
    def set_references(self):
        i = self.theory_id
        reference = {
            '*':
             {
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
        self.sanity_patterns = sn.assert_found(r'\[RESULT\]\[0]\ Case ' + str(i), self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):
        i = self.theory_id
        self.perf_patterns = {
                # metric,expression for each case
                f'flops{i}':
                sn.extractsingle(
                    r'\[RESULT\]\[0\] Case ' + str(i) +
                    r' (\S+) Gflops/seconds', 1, self.stdout),
                f'time{i}':
                sn.extractsingle(
                    r'\[RESULT\]\[0\] Case ' + str(i) +
                    r' \S+ Gflops in (\S+) seconds', 1, self.stdout),
                f'communicated{i}':
                sn.extractsingle(
                    r'\[MAIN\]\[0\] Case ' + str(i) +
                    r' .* (\S+) bytes communicated', 1, self.stdout),
                f'avg_arithmetic_intensity{i}':
                sn.extractsingle(
                    r'\[MAIN\]\[0\] Case ' + str(i) +
                    r' (\S+) average arithmetic intensity', 1, self.stdout),
                f'computation/communication{i}':
                sn.extractsingle(
                    r'\[MAIN\]\[0\] Case ' + str(i) +
                    r' (\S+) flop per byte communicated', 1, self.stdout),
            }


@rfm.simple_test
class SombreroBenchmarkMini(SombreroBenchmarkBase):
    valid_systems = ['*']
    tags = {"mini"}

    @run_after('init')
    def set_up_from_parameters(self):
        self.executable_opts = ['-l', '8x4x4x4', '-p', '2x1x1x1']
        self.num_tasks = 2
        self.extra_resources = {  # TODO: check that this can be an instance variable
            'mpi': {
                'num_slots': self.num_tasks
            }
        }

@rfm.simple_test
class SombreroBenchmarkScaling(SombreroBenchmarkBase):
    params = parameter(case_filter.generate(scaling_config))
    valid_systems = ['*']
    tags = {"scaling"}

    @run_after('init')
    def set_up_from_parameters(self):
        self.executable_opts = []
        if self.params[case_filter.Idx.strong_or_weak] == "weak":
            self.executable_opts.append('-w')
        self.executable_opts += ['-s', self.params[case_filter.Idx.size]]
        self.num_tasks = self.params[case_filter.Idx.nprocesses]
        self.extra_resources = {
            'mpi': {
                'num_slots': self.num_tasks
            }
        }

@rfm.simple_test
class SombreroITTsn(SombreroBenchmarkBase):
    valid_systems = ['*']
    tags = {"ITT-sn"}

    @run_after('init')
    def set_up_from_parameters(self):
        self.executable_opts = ['-s', 'small']
        self.num_tasks = self.current_partition.processor.num_cores
        self.extra_resources = {
            'mpi': {
                'num_slots': self.num_tasks
            }
        }

@rfm.simple_test
class SombreroITT64n(SombreroBenchmarkBase):
    valid_systems = ['*']
    tags = {"ITT-64n"}

    @run_after('init')
    def set_up_from_parameters(self):
        self.executable_opts = ['-s', 'medium']
        self.num_tasks = self.current_partition.processor.num_cores*64
        self.extra_resources = {
            'mpi': {
                'num_slots': self.num_tasks
            }
        }
