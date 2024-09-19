import reframe as rfm
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest

class PurifyBase(SpackTest):
#class PurifyBase(rfm.RunOnlyRegressionTest):

    valid_systems = ['*']
    valid_prog_environs = ['default']

    spack_spec = 'purify@develop+benchmarks^sopt@develop'
    executable_opts = ['--benchmark_format=csv', '--benchmark_out=purify_benchmark.out', '--benchmark_out_format=csv']

    num_tasks = 1
    num_cpus_per_task = 1
    env_vars = {
        'OMP_NUM_THREADS': 1
    }

    @sanity_function
    def validate_solution(self):
        return sn.assert_found(r'Running', self.stderr)

    @performance_function('ms', perf_key='mean')
    def extract_mean(self):
        return sn.extractsingle(r'manual_time_mean\",\S+,(\S+),\S+,ms', self.stdout, 1, float)

    @performance_function('ms', perf_key='median')
    def extract_median(self):
        return sn.extractsingle(r'manual_time_median\",\S+,(\S+),\S+,ms', self.stdout, 1, float)

    @performance_function('ms', perf_key='stddev')
    def extract_stddev(self):
        return sn.extractsingle(r'manual_time_stddev\",\S+,(\S+),\S+,ms', self.stdout, 1, float)

class PurifyMPIBase(PurifyBase):

    ntasks = parameter([1,2])

    @run_after('setup')
    def set_num_tasks(self):
        self.num_tasks = self.ntasks

@rfm.simple_test
class PurifyPADMMBenchmark(PurifyMPIBase):

    executable = 'mpi_benchmark_PADMM'
    time_limit = '60m'

    algorithm = parameter([1,3])
    numberOfVisibilities = parameter([10**5])
    imgsize = parameter([256])

    @run_after('setup')
    def filter_benchmarks(self):
        self.executable_opts.append(f'--benchmark_filter=PadmmFixtureMPI/'
                                    f'ApplyAlgo{self.algorithm}'
                                    f'/{self.imgsize}/{self.numberOfVisibilities}')

@rfm.simple_test
class PurifyMOBenchmark(PurifyMPIBase):

    executable = 'mpi_benchmark_MO'
    time_limit = '60m'

    #numberOfVisibilities = parameter([10**6, 5*10**6, 10**7, 5*10**7, 10**8, 5*10**8])
    #imgsize = parameter([1024])
    numberOfVisibilities = parameter([10**5])
    imgsize = parameter([256])
    FixtureName = parameter(['DirectFixtureDistr',
                             'AdjointFixtureDistr',
                             'DirectFixtureMPI',
                             'AdjointFixtureMPI'])

    @run_after('setup')
    def filter_benchmarks(self):
        self.executable_opts.append(f'--benchmark_filter={self.FixtureName}'
                                    f'/Apply/{self.imgsize}/{self.numberOfVisibilities}')

@rfm.simple_test
class PurifyFFTBenchmark(PurifyBase):

    executable = 'fft'
    time_limit = '5m'

    imgsize = parameter([2**i for i in range(7,14)])

    @run_after('setup')
    def filter_benchmarks(self):
        self.executable_opts.append(f'--benchmark_filter=FFTOperatorFixture/Apply/{self.imgsize}')
