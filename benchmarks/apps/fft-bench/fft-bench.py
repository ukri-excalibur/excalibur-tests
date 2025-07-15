import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn

from benchmarks.modules.utils import SpackTest


@rfm.simple_test
class FftBenchmarkCpu(SpackTest):
    # Systems and programming environments where to run this benchmark.
    # Systems/partitions can be identified by their features, `+feature` is a
    # partition which has the named feature, `-feature` is a partition which
    # does not have the named feature.  This is a CPU-only benchmark, so we use
    # `-gpu` to exclude GPU partitions.
    valid_systems = ['*']
    valid_prog_environs = ['default']
    tasks = parameter([1])  # Used to set `num_tasks` in `__init__`.
    num_tasks_per_node = 1
    sourcesdir = os.path.dirname(__file__)
    time_limit = '4h'


    executable = 'FFT_Bench'
    # Spack specification with default value.  A different value can be set
    # from the command line with `-S spack_spec='...'`:
    # https://reframe-hpc.readthedocs.io/en/stable/manpage.html#cmdoption-S
    spack_spec = 'fft-bench@0.2 +fft'

    # Arguments to pass to the program above to run the benchmarks.
    # -s float = Starting memory footprint in MB
    # -m int = Number of runs to do after starting memory footprint
    # -n int = Number of times to repeat a run for averaging
    # -f Run with FFTW3 Library
    # -c Run with CUDA Library
    # -r Run with RocFFT Library
    executable_opts = ["-s", "500", "-m", "4", "-n", "10", "-f"]

    reference = {
        'myriad': {
		'Libarary': ("FFTW", None, None, None),
                'Size': (1., None, None, 'MB'),
                'Time': (1., None, None, 'miliseconds'),
        }
    }

    @run_after('setup')
    def setup_variables(self):
        self.num_tasks = self.tasks
        self.num_cpus_per_task = self.cpus_per_task
        # Tags are useful for categorizing tests and quickly selecting those of interest.
        self.tags.add("fft_bench")
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
        self.sanity_patterns = sn.assert_found(r'Run_Finished', self.stdout)

    # A performance benchmark.
    @run_before('performance')
    def set_perf_patterns(self):
        # This performance pattern parses the output of the program to extract
        # the desired figure of merit.
        self.perf_patterns = {
            dict(
                sn.extract_all(
                    r'<Library>,\t\t<Size>,\t\t<Time>,',
                    self.stdout, ['Library', 'Size', 'Time'], [str, float, float])
            )
        }
