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

# Class to define the benchmark.  See
# https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#the-reframe-module
# for more information about the API of ReFrame tests.
@rfm.simple_test
class LibtreeTest(rfm.RegressionTest):
    # Systems and programming environments where to run this benchmark.  We
    # typically run them on all systems ('*'), unless there are particular
    # constraints.
    valid_systems = ['*']
    valid_prog_environs = ['*']
    # The build system to use.  We always use Spack.
    build_system = 'Spack'
    # The program to run the benchmarks.
    executable = 'libtree'
    # Arguments to pass to the program above to run the benchmarks.
    executable_opts = ['--version']
    num_tasks = 1
    num_cpus_per_task = 1
    # Time limit for the benchmark job in the scheduler.
    time_limit = '2m'
    variables = {
        'OMP_NUM_THREADS': f'{num_cpus_per_task}',
        'OMP_PLACES': 'cores'
    }
    extra_resources = {
        'mpi': {'num_slots': num_tasks * num_cpus_per_task}
    }

    # Function to install the package with Spack.
    @run_before('compile')
    def setup_build_system(self):
        # Spack spec(s) to install the desired package(s).  It is recommended
        # to specify also the version number.
        self.build_system.specs = ['libtree@2.0.0']
        # Identify the Spack environment for the current system.  Keep this
        # setting as is.
        self.build_system.environment = identify_build_environment(
            self.current_system.name)

    # Function defining a sanity check.  See
    # https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html
    # for the API of ReFrame tests, including performance ones.
    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'2.0.0', self.stdout)
