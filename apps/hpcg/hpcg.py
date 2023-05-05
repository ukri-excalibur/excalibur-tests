# Copyright 2021 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os.path as path
import sys
import reframe as rfm
import reframe.utility.sanity as sn
import glob

# Add top-level directory to `sys.path` so we can easily import extra modules
# from any directory.
sys.path.append(path.join(path.dirname(__file__), '..', '..'))
# `SpackTest` is a class for benchmarks which will use Spack as build system.
# The only requirement is to inherit this class and set the `spack_spec`
# attribute.
from modules.utils import SpackTest

# Class to define the benchmark.  See
# https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html#the-reframe-module
# for more information about the API of ReFrame tests.
#@rfm.simple_test
class HPCGBenchmark(SpackTest):
    # Systems and programming environments where to run this benchmark.  We
    # typically run them on all systems ('*'), unless there are particular
    # constraints.
    valid_systems = ['*']
    valid_prog_environs = ['default']
    num_cpus_per_task = 1
    # The program for running the benchmarks.
    executable = 'xhpcg'
    # Arguments to pass to the program above to run the benchmarks.
    executable_opts = []
    # Time limit of the job, automatically set in the job script.
    time_limit = '3m'
    # These extra resources are needed for when using the SGE scheduler.
    extra_resources = {
        'mpi': {'num_slots': num_tasks * num_cpus_per_task}
    }

    reference = {
        # flops? Gflops/s ?
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
        self.variables['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = [self.spack_spec]

    @run_before('sanity')
    def set_sanity_patterns(self):
        # Should probably check that it's a valid run
        self.sanity_patterns = sn.assert_found(r'', self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):
        # This performance pattern parses the output of the program to extract
        # the desired figure of merit.
        possible_outfiles = glob.glob(self.stagedir + "/HPCG*.txt") 
        self.output_data  = possible_outfiles[0] 
        self.perf_patterns = {
            'flops': sn.extractsingle(
                r'VALID with a GFLOP/s rating of=(\S+)',
                self.output_data, 1, float),
        }

@rfm.simple_test
class HPCG_Stencil(HPCGBenchmark):
    spack_spec = 'hpcg_excalibur'        
    num_tasks = 40
    num_tasks_per_node = 40

@rfm.simple_test
class HPCG_Original(HPCGBenchmark):
    spack_spec = 'hpcg_excalibur@hpcg_original'
    num_tasks = 40 # get this from cascade lake?
    num_tasks_per_node = 40
    
@rfm.simple_test
class HPCG_LFRic(HPCGBenchmark):
    # As above but with the LFRic style stencil
    spack_spec = 'hpcg_excalibur@hpcg_lfric'
    num_tasks = 40
    num_tasks_per_node = 40

    @run_after('compile')
    def copy_input_file(self):
        # during install a file will be copied to the spack env bin - get it and put it in stagedir
        self.prerun_cmds = ["python -c 'import shutil;import os;shutil.copyfile(shutil.which(\"xhpcg\").replace(\"xhpcg\",\"dinodump.dat\"), os.getcwd()+\"/dinodump.dat\")'"]
