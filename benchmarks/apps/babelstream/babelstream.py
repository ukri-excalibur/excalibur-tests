# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
import os
import os.path as path
import sys
import reframe as rfm
import reframe.utility.sanity as sn
from reframe.core.backends import getlauncher
# Add top-level directory to `sys.path` so we can easily import extra modules
# from any directory.
sys.path.append(path.join(path.dirname(__file__), '..', '..'))
# `SpackTest` is a class for benchmarks which will use Spack as build system.
# The only requirement is to inherit this class and set the `spack_spec`
# attribute.
from modules.utils import SpackTest



# spack install --add babelstream%gcc@9.2.0 +thrust backend=cuda cuda_arch=70
@rfm.simple_test
class BabelstreamBenchmarkBase(SpackTest):
    descr = 'Build BabelStream with Spack Build System'
    valid_systems = ['*']
    valid_prog_environs = ['default'] 
    # impl = variable(str, value='d', loggable=True)
    # impl =required
    print(impl)
    

    @run_before('run')
    def replace_launcher(self):
        # For this benchmark we don't use MPI at all, so we always force the
        # local launcher:
        # <https://reframe-hpc.readthedocs.io/en/v4.1.3/tutorial_advanced.html#replacing-the-parallel-launcher>.
        self.job.launcher = getlauncher('local')()
    
    @run_after('setup')
    def setup_variables(self):
        # self.executable_opts = [os.path.join(self.prefix, 'openmm-gpu-bench.py')]
        # self.set_var_default(
        #     'num_cpus_per_task',
        #     self.current_partition.processor.num_cpus)
        # self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'
        # self.env_vars['OMP_PLACES'] = 'cores'
        # # Needed for the SGE scheduler
        # self.extra_resources['mpi'] = {'num_slots': self.num_tasks * self.num_cpus_per_task}
        # Request the GPU resources necessary to run this job.
        self.extra_resources['gpu'] = {'num_gpus_per_node': self.num_gpus_per_node}

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found('Running kernels 100 times', self.stdout)

#    @run_before('performance')
#     def set_perf_patterns(self):
#         self.perf_patterns = {
#             'speed': sn.extractsingle(
#                 r'^100\.0%(?:[ \t]+[-\d.]+){5}[ \t]+([-\d.]+)[ \t]+[\d:]+$',
#                 self.stdout, 1, float),
#         }

# Python's built-in float type has double precision (it's a C double in CPython, a Java double in Jython).
# If you need more precision, get NumPy and use its numpy.float128.
    @performance_function('MBytes/sec', perf_key='Copy')
    def extract_copy_perf(self):
        return sn.extractsingle(r'Copy \s+(\S+)\s+.', self.stdout, 1, float)

    @performance_function('MBytes/sec', perf_key='Mul')
    def extract_scale_perf(self):
        return sn.extractsingle(r'Mul \s+(\S+)\s+..', self.stdout, 1, float)

    @performance_function('MBytes/sec', perf_key='Add')
    def extract_add_perf(self):
        return sn.extractsingle(r'Add \s+(\S+)\s+.?', self.stdout, 1, float)

    @performance_function('MBytes/sec', perf_key='Triad')
    def extract_triad_perf(self):
        return sn.extractsingle(r'Triad \s+(\S+)\s+.', self.stdout, 1, float)
    @performance_function('MBytes/sec', perf_key='Dot')
    def extract_dot_perf(self):
        return sn.extractsingle(r'Dot \s+(\S+)\s+.', self.stdout, 1, float)


@rfm.simple_test
class ACCBenchmark(BabelstreamBenchmarkBase):
    valid_systems = ['*']
    tags = {"acc"}
    
    executable = "acc-stream"
    num_gpus_per_node = 1
    # modules=['cudatoolkit']
    # environment = "~/excalibur-tests/benchmarks/spack/isambard-macs/cascadelake/"


@rfm.simple_test
class CUDABenchmark(BabelstreamBenchmarkBase):
    valid_systems = ['*']
    tags = {"cuda"}
    executable = "cuda-stream"
    valid_systems = ['+gpu']
    num_gpus_per_node = 1
    # environment = "~/excalibur-tests/benchmarks/spack/isambard-macs/volta"

@rfm.simple_test
class OCLBenchmark(BabelstreamBenchmarkBase):
    valid_systems = ['*']
    tags = {"ocl"}
    executable = "ocl-stream"
    valid_systems = ['+gpu']
    num_gpus_per_node = 1
# @rfm.simple_test
# class CUDABenchmark(BabelstreamBenchmarkBase):
#     valid_systems = ['*']
#     tags = {"cuda"}
#     executable = "cuda-stream"
#     valid_systems = ['+gpu']
#     num_gpus_per_node = 1

#     @run_after('init')
#     def set_up_from_parameters(self):
#         # self.executable_opts = ['-l', '8x4x4x4', '-p', '2x1x1x1']
#         # self.num_tasks = 2
#         # self.extra_resources = {'mpi': {'num_slots': self.num_tasks}}

    



