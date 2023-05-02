# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause

import os.path as path
import sys
import reframe as rfm
import reframe.utility.sanity as sn

# Add top-level directory to `sys.path` so we can easily import extra modules
# from any directory.
sys.path.append(path.join(path.dirname(__file__), '..', '..'))
# `SpackTest` is a class for benchmarks which will use Spack as build system.
# The only requirement is to inherit this class and set the `spack_spec`
# attribute.
from modules.utils import SpackTest

@rfm.simple_test
class BabelstreamBenchmark(SpackTest):
    descr = 'Demo test using Spack to build the test code'
    valid_systems = ['*']
    valid_prog_environs = ['builtin']
    executable = 'babelstream'
    executable_opts = ['--help']
    build_system = 'Spack'

# spack install --add babelstream%gcc@9.2.0 +thrust backend=cuda cuda_arch=70

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = ['babelstream@develop%gcc@9.2.0 +thrust implementation=cuda cuda_arch=70']

    @sanity_function
    def assert_version(self):
        return sn.assert_found(r'Version 4.0.4', self.stderr)