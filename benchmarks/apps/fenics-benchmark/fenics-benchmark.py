# Copyright 2023 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os.path as path
import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
import glob

# `SpackTest` is a class for benchmarks which will use Spack as build system.
# The only requirement is to inherit this class and set the `spack_spec`
# attribute.
from benchmarks.modules.utils import SpackTest

@rfm.simple_test
class FEniCSBenchmark(SpackTest):
    spack_spec = "fenics-benchmark@0.6.0"
    valid_systems = ['-gpu']
    valid_prog_environs = ['default']
    num_cpus_per_task = 1
    num_tasks = 8
    num_tasks_per_node = 8

    # The program for running the benchmarks.
    executable = 'dolfinx-scaling-test'
    # Arguments to pass to the program above to run the benchmarks.
    executable_opts = [
        "--problem_type poisson",
        "--scaling_type weak",
        "--ndofs 500000", # 500000
        "-log_view",
        "-ksp_view",
        "-ksp_type cg",
        "-ksp_rtol 1.0e-8",
        "-pc_type hypre",
        "-pc_hypre_type boomeramg",
        "-pc_hypre_boomeramg_strong_threshold 0.7",
        "-pc_hypre_boomeramg_agg_nl 4",
        "-pc_hypre_boomeramg_agg_num_paths 2",
        "-options_left",
        ]

    # Time limit of the job, automatically set in the job script.
    time_limit = '3m'

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found("Test problem summary", self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):
        # This performance pattern parses the output of the program to extract
        # the desired figure of merit.

        metrics = [ "Create boundary conditions",
            "Create RHS function",
            "Assemble matrix",
            "Assemble vector", "Create Mesh",
            "FunctionSpace", "Solve"]

        self.perf_patterns = {
            m: sn.extractsingle(
                "ZZZ " + m + r"\s+\|\s+\d+\s+(?P<time>\d+\.\d+).*", self.stdout, "time", float
            )
            for m in metrics
        }
