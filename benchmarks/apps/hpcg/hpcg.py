# Copyright 2021 University College London (UCL) Research Software Development
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

class HPCGBenchmark(SpackTest):
    valid_systems = ['-gpu']
    valid_prog_environs = ['default']
    num_cpus_per_task = 1
    num_tasks = required
    num_tasks_per_node = required

    # The program for running the benchmarks.
    executable = 'xhpcg'
    # Arguments to pass to the program above to run the benchmarks.
    executable_opts = []
    # Time limit of the job, automatically set in the job script.
    time_limit = '3m'
    # hpcg.dat sets size of grid
    prerun_cmds.append('cp "$(dirname $(which xhpcg))/hpcg.dat" .')

    reference = {
        'archer2': {
            'flops': (1000.0, -0.2, None, 'Gflops/seconds'),
        },
        '*': {
            'flops': (1, None, None, 'Gflops/seconds'),
        }
    }

    @run_after('setup')
    def setup_variables(self):
        # Strictly HPCG is only intended to run for 1 OMP thread, except in original version
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'


    @run_after('run')
    def set_output_datafile(self):
        # If other outputfiles in stage directory before running, ensure use latest one
        possible_outfiles = glob.glob(self.stagedir + "/HPCG*.txt")
        if (len(possible_outfiles) >= 1):
            ordered_outfiles = sorted(possible_outfiles, key=lambda t: os.stat(t).st_mtime)
            self.output_data  = ordered_outfiles[-1]
        else:
            self.output_data = '' #no data

    @run_before('sanity')
    def set_sanity_patterns(self):
        # Check that it's a valid run
        self.sanity_patterns = sn.assert_found(r'VALID with a GFLOP/s rating of=', self.output_data)

    @run_before('performance')
    def set_perf_patterns(self):
        # This performance pattern parses the output of the program to extract
        # the desired figure of merit.
        self.perf_patterns = {
            'flops': sn.extractsingle(
                r'VALID with a GFLOP/s rating of=(\S+)',
                self.output_data, 1, float),
        }

    @run_after('setup')
    def setup_num_tasks(self):
        self.set_var_default(
            'num_tasks',
            self.current_partition.processor.num_cpus //
            min(1, self.current_partition.processor.num_cpus_per_core) //
            self.num_cpus_per_task)
        self.set_var_default('num_tasks_per_node',
                             self.current_partition.processor.num_cpus //
                             self.num_cpus_per_task)


@rfm.simple_test
class HPCG_Stencil(HPCGBenchmark):
    spack_spec = 'hpcg_excalibur@hpcg_stencil'
    tags = {"27pt_stencil"}

@rfm.simple_test
class HPCG_Original(HPCGBenchmark):
    spack_spec = 'hpcg_excalibur@hpcg_original'
    tags = {"27pt_stencil"}

@rfm.simple_test
class HPCG_LFRic(HPCGBenchmark):
    # As above but with the LFRic style stencil
    spack_spec = 'hpcg_excalibur@hpcg_lfric'
    tags = {"lfric"}
    # lfric app requires extra data - dinodump.dat
    prerun_cmds.append('cp "$(dirname $(which xhpcg))/dinodump.dat" .')
