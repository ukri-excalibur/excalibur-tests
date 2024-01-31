# Copyright 2016-2022 Swiss National Supercomputing Centre (CSCS/ETH Zurich)
# ReFrame Project Developers. See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: BSD-3-Clause
import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.osext as osext
from reframe.core.backends import getlauncher
# `SpackTest` is a class for benchmarks which will use Spack as build system.
# The only requirement is to inherit this class and set the `spack_spec`
# attribute.
from benchmarks.modules.utils import SpackTest


@rfm.simple_test
class BabelstreamBenchmarkBase(SpackTest):
    descr = 'Build BabelStream with Spack Build System'
    compiler_version =  variable(str, value='', loggable=True)
    compiler_name =  variable(str, value='', loggable=True)
    valid_systems = ['*']
    valid_prog_environs = ['default']
    # Time limit of the job, automatically set in the job script.
    time_limit = '15m'
    @run_before('run')
    def replace_launcher(self):
        # For this benchmark we don't use MPI at all, so we always force the
        # local launcher:
        # <https://reframe-hpc.readthedocs.io/en/v4.1.3/tutorial_advanced.html#replacing-the-parallel-launcher>.
        self.job.launcher = getlauncher('local')()
    @run_after('setup')
    def setup_variables(self):
        # Request the GPU resources necessary to run this job.
        self.extra_resources['gpu'] = {'num_gpus_per_node': self.num_gpus_per_node}
    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found('Running kernels 100 times', self.stdout)
    # @run_after('run')
    # def get_compiler_version(self):
    #     with osext.change_dir(self.stagedir):
    #         self.compiler_version = sn.extractsingle(r'(.*(?:\((?:G|I)CC\)|version) .*)', self.stdout, 1).evaluate()
   #--------------------------------------------------
    #-- Figure of Merit Export
    #--------------------------------------------------
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
    @run_after('run')
    def get_compiler_name(self):
        with osext.change_dir(self.stagedir):
            self.compiler_name = sn.extractsingle(r'compilerName:\s*(\S+)', self.stdout, 1).evaluate()
    @run_after('run')
    def get_compiler_version(self):
        with osext.change_dir(self.stagedir):
            self.compiler_version = sn.extractsingle(r'compilerVersion:\s*(\S+)', self.stdout, 1).evaluate()

    @run_after('setup')
    def setup_num_tasks(self):
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'

#--------------------------------------------------
#-- ACC
#--------------------------------------------------
@rfm.simple_test
class ACCBenchmark_CPU(BabelstreamBenchmarkBase):
    valid_systems = ['-gpu']
    tags = {"acc"}
    executable = "acc-stream"

@rfm.simple_test
class ACCBenchmark_GPU(BabelstreamBenchmarkBase):
    valid_systems = ['+gpu +cuda']
    tags = {"acc"}
    executable = "acc-stream"
    num_gpus_per_node = 1
#--------------------------------------------------
#-- CUDA
#--------------------------------------------------
@rfm.simple_test
class CUDABenchmark(BabelstreamBenchmarkBase):
    valid_systems = ['+gpu +cuda']
    tags = {"cuda"}
    executable = "cuda-stream"
    num_gpus_per_node = 1
#--------------------------------------------------
#-- OpenCL
#--------------------------------------------------
@rfm.simple_test
class OCLBenchmark_CPU(BabelstreamBenchmarkBase):
    valid_systems = ['-gpu']
    tags = {"ocl"}
    executable = "ocl-stream"

@rfm.simple_test
class OCLBenchmark_GPU(BabelstreamBenchmarkBase):
    valid_systems = ['+gpu']
    tags = {"ocl"}
    executable = "ocl-stream"
    num_gpus_per_node = 1
#--------------------------------------------------
#-- Kokkos
#--------------------------------------------------
@rfm.simple_test
class KOKKOSBenchmark_CPU(BabelstreamBenchmarkBase):
    valid_systems = ['-gpu']
    tags = {"kokkos"}
    executable = "kokkos-stream"

@rfm.simple_test
class KOKKOSBenchmark_GPU(BabelstreamBenchmarkBase):
    valid_systems = ['+gpu']
    tags = {"kokkos"}
    executable = "kokkos-stream"
    num_gpus_per_node = 1
#--------------------------------------------------
#-- TBB
#--------------------------------------------------
@rfm.simple_test
class TBBBenchmark(BabelstreamBenchmarkBase):
    valid_systems = ['-gpu']
    tags = {"tbb"}
    executable = "tbb-stream"
#--------------------------------------------------
#-- Thrust
#--------------------------------------------------
@rfm.simple_test
class THRUSTBenchmark_NVIDIA(BabelstreamBenchmarkBase):
    valid_systems = ['+gpu +cuda']
    tags = {"thrust"}
    executable = "thrust-stream"
    num_gpus_per_node = 1

@rfm.simple_test
class THRUSTBenchmark_AMD(BabelstreamBenchmarkBase):
    valid_systems = ['+gpu +rocm']
    tags = {"thrust"}
    executable = "thrust-stream"
    num_gpus_per_node = 1
#--------------------------------------------------
#-- RAJA
#--------------------------------------------------
@rfm.simple_test
class RAJABenchmark_CPU(BabelstreamBenchmarkBase):
    valid_systems = ['-gpu']
    tags = {"raja"}
    executable = "raja-stream"

@rfm.simple_test
class RAJABenchmark_GPU(BabelstreamBenchmarkBase):
    valid_systems = ['+gpu']
    tags = {"raja"}
    executable = "kokkos-stream"
    num_gpus_per_node = 1
#--------------------------------------------------
#-- OpenMP
#--------------------------------------------------
@rfm.simple_test
class OMPBenchmark_CPU(BabelstreamBenchmarkBase):
    valid_systems = ['-gpu']
    tags = {"omp"}
    executable = "omp-stream"

@rfm.simple_test
class OMPBenchmark_NVIDIA(BabelstreamBenchmarkBase):
    valid_systems = ['+gpu +cuda']
    tags = {"omp"}
    executable = "omp-stream"
    num_gpus_per_node = 1

@rfm.simple_test
class OMPBenchmark_AMD(BabelstreamBenchmarkBase):
    valid_systems = ['+gpu +rocm']
    tags = {"omp"}
    executable = "omp-stream"
    num_gpus_per_node = 1

#--------------------------------------------------
#-- std-data,ranges,indices
#--------------------------------------------------
@rfm.simple_test
class STDDATABenchmark(BabelstreamBenchmarkBase):
    valid_systems = ['-gpu']
    tags = {"std-data"}
    executable = "std-data-stream"
@rfm.simple_test
class STDDATABenchmark_NVIDIA(BabelstreamBenchmarkBase):
    valid_systems = ['+gpu +cuda']
    tags = {"std-data"}
    executable = "std-data-stream"
    num_gpus_per_node = 1
#--------------------------------------------------
#-- std-data,ranges,indices
#--------------------------------------------------
@rfm.simple_test
class STDRANGESBenchmark(BabelstreamBenchmarkBase):
    valid_systems = ['-gpu']
    tags = {"std-ranges"}
    executable = "std-ranges-stream"
@rfm.simple_test
class STDRANGESBenchmark_NVIDIA(BabelstreamBenchmarkBase):
    valid_systems = ['+gpu +cuda']
    tags = {"std-ranges"}
    executable = "std-ranges-stream"
    num_gpus_per_node = 1
#--------------------------------------------------
#-- std-data,ranges,indices
#--------------------------------------------------
@rfm.simple_test
class STDINDICESBenchmark(BabelstreamBenchmarkBase):
    valid_systems = ['-gpu']
    tags = {"std-indices"}
    executable = "std-indices-stream"
@rfm.simple_test
class STDINDICESBenchmark_NVIDIA(BabelstreamBenchmarkBase):
    valid_systems = ['+gpu +cuda']
    tags = {"std-indices"}
    executable = "std-indices-stream"
    num_gpus_per_node = 1
#--------------------------------------------------
#-- SYCL2020
#--------------------------------------------------
@rfm.simple_test
class SYCL2020Benchmark(BabelstreamBenchmarkBase):
    valid_systems = ['-gpu']
    tags = {"sycl2020"}
    executable = "sycl2020-stream"
#--------------------------------------------------
#-- SYCL
#--------------------------------------------------
@rfm.simple_test
class SYCLBenchmark(BabelstreamBenchmarkBase):
    valid_systems = ['-gpu']
    tags = {"sycl"}
    executable = "sycl-stream"
#--------------------------------------------------
#-- HIP(ROCm)
#--------------------------------------------------
@rfm.simple_test
class HIPBenchmark(BabelstreamBenchmarkBase):
    valid_systems = ['+gpu +rocm']
    tags = {"hip"}
    executable = "hip-stream"
