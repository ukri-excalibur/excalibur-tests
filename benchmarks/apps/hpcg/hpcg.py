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


# TODO - make a class which inherits the above, then uses spack to install oneapi mkl and so on
# for paper on Isambard this is hard loaded below due to issues on the system (see other github issues)

from reframe.core.backends import getlauncher
from reframe.core.pipeline import RunOnlyRegressionTest

class HPCGIntelOptimised_Isambard(RunOnlyRegressionTest):
    valid_systems = ['*'] #- isambard only
    valid_prog_environs = ['*'] # again - all hard-coded on Isambard
    executable = './xhpcg'
    num_cpus_per_task = 1
    num_tasks = required
    num_tasks_per_node = required
    time_limit = '40m'
    maintainers = ['dcaseGH']
    prerun_cmds.append('module use --append /projects/bristol/modules/intel-oneapi-2023.1.0/tbb/2021.9.0/modulefiles')
    prerun_cmds.append('module use --append /projects/bristol/modules/intel-oneapi-2023.1.0/mpi/2021.9.0/modulefiles')
    prerun_cmds.append('module use --append /projects/bristol/modules/intel-oneapi-2023.1.0/mkl/2023.1.0/modulefiles')
    prerun_cmds.append('module use --append /projects/bristol/modules/intel-oneapi-2023.1.0/compiler/2023.1.0/modulefiles')
    prerun_cmds.append('module load mkl')
    prerun_cmds.append('module load mpi')
    prerun_cmds.append('cp /home/mox-dcase/small.dat hpcg.dat') # Strictly dont need this, but following the above lead to copy dat

    @run_after('run')
    def set_output_datafile(self):
        # If other outputfiles in stage directory before running, ensure use latest one
        # Assume using 104 ** 3 grid
        possible_outfiles = glob.glob(self.stagedir + "/n104*.txt")
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

    @run_before('run')
    def setup_variables(self):
        # Strictly HPCG is only intended to run for 1 OMP thread, except in original version
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'
        
    @run_before('run')
    def set_launcher(self):
        self.job.launcher = getlauncher('mpiexec')()

    @run_before('run')
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
class HPCG_IntelAVX_Isambard(HPCGIntelOptimised_Isambard):
    # Copy the avx exe and run it
    tags = {"intel", "avx"}
    prerun_cmds.append('cp /projects/bristol/modules/intel-oneapi-2023.1.0/mkl/2023.1.0/benchmarks/hpcg/bin/xhpcg_avx xhpcg')

@rfm.simple_test
class HPCG_IntelAVX2_Isambard(HPCGIntelOptimised_Isambard):
    # Copy the avx2 exe and run it
    tags = {"intel", "avx2"}
    prerun_cmds.append('cp /projects/bristol/modules/intel-oneapi-2023.1.0/mkl/2023.1.0/benchmarks/hpcg/bin/xhpcg_avx2 xhpcg')

@rfm.simple_test
class HPCG_IntelSKX_Isambard(HPCGIntelOptimised_Isambard):
    # Copy the skx exe and run it
    tags = {"intel", "skx"}
    prerun_cmds.append('cp /projects/bristol/modules/intel-oneapi-2023.1.0/mkl/2023.1.0/benchmarks/hpcg/bin/xhpcg_skx xhpcg')
