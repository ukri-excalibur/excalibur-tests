# Demo class for running the stream benchmark
# Used for tutorial

# Import modules from reframe and excalibur-tests
import reframe as rfm
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest

@rfm.simple_test
class StreamBenchmark(SpackTest):

    # Run configuration
    ## Mandatory ReFrame setup
    valid_systems = ['*']
    valid_prog_environs = ['default']

    ## Executable
    executable = 'stream_c.exe'
    executable_opts = ['']

    ## Scheduler options
    num_tasks = 1

    time_limit = '5m'
    num_cpus_per_task = 128
    env_vars = {
        'OMP_NUM_THREADS': f'{num_cpus_per_task}',
        'OMP_PLACES': 'cores'
    }
    use_multithreading = False

    ## Reference performance values for Archer2
    reference = {
        'archer2': {
            'Copy':  (260000, -0.25, 0.25, 'MB/s'),
            'Scale': (200000, -0.25, 0.25, 'MB/s'),
            'Add':   (200000, -0.25, 0.25, 'MB/s'),
            'Triad': (200000, -0.25, 0.25, 'MB/s')
        }
    }

    ## Build configuration
    ## Comment/uncomment the appropriate one

    # # Basic build configuration with OpenMP threads
    # spack_spec = 'stream@5.10 +openmp'

    # Build configuration with large array size to avoid caching
    spack_spec = 'stream@5.10 +openmp stream_array_size=64000000'

    # # Build configuration parametrized to scan over array sizes
    # array_size = parameter(int(i) for i in [8e6,16e6,32e6,64e6,128e6])
    # def __init__(self):
    #     self.spack_spec = f"stream@5.10 +openmp stream_array_size={self.array_size}"

    # Sanity check
    @sanity_function
    def validate_solution(self):
        return sn.assert_found(r'Solution Validates', self.stdout)

    # Performance metrics
    @performance_function('MB/s', perf_key='Copy')
    def extract_copy_perf(self):
        return sn.extractsingle(r'Copy:\s+(\S+)\s+.*', self.stdout, 1, float)

    @performance_function('MB/s', perf_key='Scale')
    def extract_scale_perf(self):
        return sn.extractsingle(r'Scale:\s+(\S+)\s+.*', self.stdout, 1, float)

    @performance_function('MB/s', perf_key='Add')
    def extract_add_perf(self):
        return sn.extractsingle(r'Add:\s+(\S+)\s+.*', self.stdout, 1, float)

    @performance_function('MB/s', perf_key='Triad')
    def extract_triad_perf(self):
        return sn.extractsingle(r'Triad:\s+(\S+)\s+.*', self.stdout, 1, float)
