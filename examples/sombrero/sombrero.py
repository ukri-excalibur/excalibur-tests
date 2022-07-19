# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os.path as path
import sys
import reframe as rfm
import reframe.utility.sanity as sn

# Add top-level directory to `sys.path` so we can easily import extra modules
# from any directory.
sys.path.append(path.join(path.dirname(__file__), '..', '..'))
# `identify_build_environment` will be used to identify the Spack environment
# to be used when running the benchmark.
from modules.utils import identify_build_environment

# See ReFrame documentation about writing tests for more details.  In
# particular:
# * https://reframe-hpc.readthedocs.io/en/stable/tutorials.html (this is a
#   walkthrough guide for writing your first tests)
# * https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html
#   (reference about the regression tests API)

class SpackSetup(rfm.RegressionTest):
    build_system = 'Spack'
    spack_spec = variable(str, value='', loggable=True)

    @run_before('compile')
    def setup_spack_environment(self):
        env_dir, cp_dir, subdir = identify_build_environment(
            self.current_partition)
        dest = path.join(self.stagedir, 'spack_env')
        self.build_system.environment = path.join(dest, subdir)
        self.prebuild_cmds = [
            f'cp -arv {cp_dir} {dest}',
            f'spack config add "config:install_tree:root:{env_dir}/opt/spack"',
        ]

    # @run_before('sanity')
    # def set_sanity_patterns(self):
    #     self.sanity_patterns = sn.assert_true(1)

# Class to define the benchmark.  See
# https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#the-reframe-module
# for more information about the API of ReFrame tests.
@rfm.simple_test
class SombreroBenchmark(SpackSetup):
    # Systems and programming environments where to run this benchmark.  We
    # typically run them on all systems ('*'), unless there are particular
    # constraints.
    valid_systems = ['*']
    valid_prog_environs = ['default']
    # Spack specification with default value.  A different value can be set
    # from the command line with `-S spack_spec='...'`:
    # https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-S
    spack_spec = 'sombrero@2021-08-16'
    # Number of (MPI) tasks and CPUs per task.  Here we hard-code 1, but in
    # other cases you may want to use something different.  Note: ReFrame will
    # automatically launch MPI with the given number of tasks, using the
    # launcher specificed in the config for the current system.
    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 1
    # The program for running the benchmarks.
    executable = 'sombrero1'
    # Arguments to pass to the program above to run the benchmarks.
    executable_opts = ['-w', '-s', 'small']
    # Time limit of the job, automatically set in the job script.
    time_limit = '2m'
    # With `variables` you can set environment variables to be used in the job.
    # For example with `OMP_NUM_THREADS` we set the number of OpenMP threads
    # (not actually used in this specific benchmark).
    variables = {
        'OMP_NUM_THREADS': f'{num_cpus_per_task}',
    }
    # These extra resources are needed for when using the SGE scheduler.
    extra_resources = {
        'mpi': {'num_slots': num_tasks * num_cpus_per_task}
    }
    # Reference values for the performance benchmarks, see the
    # `set_perf_patterns` function below.
    reference = {
        # `reference` is a dictionary, to add reference values for different
        # systems.  The keys of the dictionary will match the `system:partition`
        # you're running the benchmarks on.  The values are dictionaries, where
        # the key is the name of the performance benchmark, and the value is the
        # list of reference values: first element is the reference value, second
        # and third elements are the lower and upper thresholds as fractions (if
        # `None`, there are no bounds), last element is the unit.  See
        # https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#reframe.core.pipeline.RegressionTest.reference
        # for more information.  The key `*` matches all systems/partitions not
        # matched by the other entries of the dictionary and can be used to
        # provide a default reference value.
        'cosma8': {
            'flops': (3.8, -0.2, None, 'Gflops/seconds'),
        },
        'csd3:skylake': {
            'flops': (1.2, -0.2, None, 'Gflops/seconds'),
        },
        'csd3:icelake': {
            'flops': (1.5, -0.2, None, 'Gflops/seconds'),
        },
        'dial3': {
            'flops': (1.2, -0.2, None, 'Gflops/seconds'),
        },
        'github-actions': {
            'flops': (0.9, None, None, 'Gflops/seconds'),
        },
        'myriad': {
            'flops': (1, -0.2, None, 'Gflops/seconds'),
        },
        'tesseract': {
            'flops': (0.75, -0.2, None, 'Gflops/seconds'),
        },
        '*': {
            'flops': (1, None, None, 'Gflops/seconds'),
        }
    }

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = [self.spack_spec]

    # Function defining a sanity check.  See
    # https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html
    # for the API of ReFrame tests, including performance ones.
    @run_before('sanity')
    def set_sanity_patterns(self):
        # Check that the string `[RESULT][0]` appears in the standard outout of
        # the program.
        self.sanity_patterns = sn.assert_found(r'\[RESULT\]\[0\]', self.stdout)

    # A performance benchmark.
    @run_before('performance')
    def set_perf_patterns(self):
        # This performance pattern parses the output of the program to extract
        # the desired figure of merit.
        self.perf_patterns = {
            'flops': sn.extractsingle(
                r'\[RESULT\]\[0\] Case 1 (\S+) Gflops/seconds',
                self.stdout, 1, float),
        }
