import os.path as path
import sys
import reframe as rfm
import reframe.utility.sanity as sn

# `SpackTest` is a class for benchmarks which will use Spack as build system.
# The only requirement is to inherit this class and set the `spack_spec`
# attribute.
from benchmarks.modules.utils import SpackTest

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
class FftBenchmarkCpu(SpackTest):
    # Systems and programming environments where to run this benchmark.
    # Systems/partitions can be identified by their features, `+feature` is a
    # partition which has the named feature, `-feature` is a partition which
    # does not have the named feature.  This is a CPU-only benchmark, so we use
    # `-gpu` to exclude GPU partitions.
    valid_systems = ['']
    valid_prog_environs = ['default']
    # Spack specification with default value.  A different value can be set
    # from the command line with `-S spack_spec='...'`:
    # https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-S
    spack_spec = 'fft-bench@0.1+fft'

    # Number of (MPI) tasks and CPUs per task.  Here we parametrise them to be
    # either 1 or 2, but in other cases you may want to use something different.
    # Note: ReFrame will automatically launch MPI with the given number of tasks,
    # using the launcher specificed in the config for the current system.
    tasks = parameter([1])  # Used to set `num_tasks` in `__init__`.
    num_tasks_per_node = 1

    # Number of CPU cores to use per task.
    #cpus_per_task = parameter([8])  # Used to set `num_cpus_per_task` in `__init__`.

    # The program for running the benchmarks.
    executable = 'FFT_Bench'

    # Arguments to pass to the program above to run the benchmarks.
    # -s float = Starting memory footprint in MB
    # -m int = Number of runs to do after starting memory footprint
    # -n int = Number of times to repeat a run for averaging
    # -f Run with FFTW3 Library
    # -c Run with CUDA Library
    # -r Run with RocFFT Library
    executable_opts = ["-s", "500", "-m", "4", "-n", "10", "-f"]
    # Time limit of the job, automatically set in the job script.
    time_limit = '4h'
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
            'flops': (8.0, -0.2, None, 'Gflops/seconds'),
        }
    }

    def __init__(self):
        # The number of tasks and CPUs per task need to be set here because
        # accessing a test parameter from the class body is not allowed.
        self.num_tasks = self.tasks
        self.num_cpus_per_task = self.cpus_per_task
        # Tags are useful for categorizing tests and quickly selecting those of interest.
        self.tags.add("fft_bench")

    @run_after('setup')
    def setup_variables(self):
        # With `env_vars` you can set environment variables to be used in the
        # job.  For example with `OMP_NUM_THREADS` we set the number of OpenMP
        # threads (not actually used in this specific benchmark).  Note that
        # this has to be done after setup because we need to add entries to
        # ReFrame built-in `env_vars` variable.
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'

    # Function defining a sanity check.  See
    # https://reframe-hpc.readthedocs.io/en/stable/regression_test_api.html
    # for the API of ReFrame tests, including performance ones.
    @run_before('sanity')
    def set_sanity_patterns(self):
        # Check that the string `[FFT_Code][0]` appears in the standard output of
        # the program.
        self.sanity_patterns = sn.assert_found(r'Run_Count', self.stdout)

    # A performance benchmark.
    @run_before('performance')
    def set_perf_patterns(self):
        # This performance pattern parses the output of the program to extract
        # the desired figure of merit.
        self.perf_patterns = {
            'FFTW': sn.extractsingle(
                r'FFTW,\t\t\d{3,},\t\t\d{2,}.\d{0,}',
                self.stdout, 0, str),
        }

@rfm.simple_test
class FftBenchmarkMkl(SpackTest):
    valid_systems = ['']
    spack_spec = 'fft-bench@0.1+mkl'
    executable_opts = ["-s", "500", "-m", "4", "-n", "10", "-f"]


@rfm.simple_test
class FftBenchmarkCuda(FftBenchmarkCpu):
    valid_systems = ['cuda']
    spack_spec = 'fft-bench@0.1+cuda'
    executable_opts = ["-s", "500", "-m", "4", "-n", "10", "-f", "-c"]

    @run_before('performance')
    def set_perf_patterns(self):
        # This performance pattern parses the output of the program to extract
        # the desired figure of merit.
        self.perf_patterns = {
            'FFTW': sn.extract_all(
                r'FFTW,\t\t\d{3,},\t\t\d{2,}.\d{0,}',
                self.stdout, 0, str),
            'CUDA': sn.extractsingle(
                r'CUDA,\t\t\d{3,},\t\t\d{2,}.\d{0,}',
                self.stdout, 0, str),
        }
