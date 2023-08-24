# Demo class for running the amg benchmark
# RSECon2023 Reframe workshop

# Import modules from reframe and excalibur-tests
import reframe as rfm
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest

@rfm.simple_test
class StreamBenchmark(SpackTest):

    # Run configuration
    ## Mandatory ReFrame setup
    valid_systems = ['archer2']
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

    ## Reference performance values
    reference = {
        'archer2': {
            'Copy':  (130000, -0.25, 0.25, 'MB/s'),
            'Scale': (100000, -0.25, 0.25, 'MB/s'),
            'Add':   (100000, -0.25, 0.25, 'MB/s'),
            'Triad': (100000, -0.25, 0.25, 'MB/s')
        }
    }

    ## Build configuration
    ## Comment/uncomment the appropriate one
    
    # Basic build configuration
    spack_spec = 'stream@5.10 +openmp'
    
    # Build configuration with optimized array size
    spack_spec = 'stream@5.10 +openmp stream_array_size=64000000'

    # Parametrized build configuration
    array_size = parameter(int(i) for i in [4e6,8e6,16e6,32e6,64e6])
    def __init__(self):
        self.spack_spec = f"stream@5.10 +openmp stream_array_size={self.array_size}"

    # Performance tuning by passing system specific scheduler options
    @run_before('run')
    def set_cpu_binding(self):
        if self.current_system.name == 'archer2':
            self.job.launcher.options = ['--distribution=block:block --hint=nomultithread']

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
