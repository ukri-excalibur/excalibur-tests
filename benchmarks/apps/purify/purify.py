import reframe as rfm
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest

class PurifyBase(SpackTest):

    num_tasks = required
    num_cpus_per_task = required

    valid_systems = ['*']
    valid_prog_environs = ['default']

    spack_spec = 'purify@4.2.0+benchmarks'
    executable_opts = ['--benchmark_format=csv',
                       '--benchmark_out=purify_benchmark.out',
                       '--benchmark_out_format=csv']

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



@rfm.simple_test
class PurifyFFTBenchmark(PurifyBase):
    """
    Execute all the benchmarks in the fft benchmark on one core with one thread
    """

    num_tasks = 1
    num_cpus_per_task = 1
    env_vars['OMP_NUM_THREADS'] = '1'

    executable = "fft"
    time_limit = '5m'

    imgsize = parameter([2**i for i in range(7,14)])

    @run_after('setup')
    def filter_benchmarks(self):
        self.executable_opts.append(f'--benchmark_filter=FFTOperatorFixture/Apply/{self.imgsize}')

@rfm.simple_test
class PurifyMOBenchmark(PurifyBase):
    """
    Execute all the benchmarks in mpi_benchmark_MO on one core with 16 threads
    (Probably not the greatest idea).
    """

    num_tasks = 1
    num_cpus_per_task = 1
    env_vars['OMP_NUM_THREADS'] = '16'

    executable = 'mpi_benchmark_MO'
    time_limit = '60m'

    numberOfVisibilities = parameter([10**6, 5*10**6, 10**7, 5*10**7, 10**8, 5*10**8])
    imgsize = parameter([1024])
    FixtureName = parameter(['DirectFixtureDistr',
                             'AdjointFixtureDistr',
                             'DirectFixtureMPI',
                             'AdjointFixtureMPI'])

    def filter_benchmarks(self):
        self.executable_opts.append(f'--benchmark_filter={self.FixtureName}'
                                    f'/Apply/{self.imgsize}/{self.numberOfVisibilities}/')

@rfm.simple_test
class PurifyMOBenchmark_PratleyEtAl(PurifyBase):
    """
    This benchmark reproduces the results in Figure 1 of Pratley et. al. Procedia Computer Science 00 (2019) 1–25
    """

    threads = 16
    tasks = parameter([1,2,3,4,8,12])

    executable = 'mpi_benchmark_MO'
    time_limit = '60m'

    numberOfVisibilities = parameter([10**6, 10**7])
    imgsize = parameter([1024])
    FixtureName = parameter(['DirectFixtureDistr',
                             'AdjointFixtureDistr',
                             'DirectFixtureMPI',
                             'AdjointFixtureMPI'])

    @run_after('setup')
    def filter_benchmarks(self):
        self.executable_opts.append(f'--benchmark_filter={self.FixtureName}'
                                    f'/Apply/{self.imgsize}/{self.numberOfVisibilities}/')
        self.executable_opts.append(f'--benchmark_min_time=20s')
        self.env_vars['OMP_NUM_THREADS'] = f'{self.threads}'
        self.num_tasks = self.tasks
        self.num_cpus_per_task = self.threads
        self.num_tasks_per_node = 1

@rfm.simple_test
class PurifyPADMMBenchmark_PratleyEtAl(PurifyBase):
    """
    This benchmark reproduces the results in Figure 3 of Pratley et. al. Procedia Computer Science 00 (2019) 1–25
    """
    threads = 16
    tasks = parameter([1,2,3,4,8,12])

    executable = 'mpi_benchmark_PADMM'
    time_limit = '60m'

    algorithm = parameter([1,3])
    numberOfVisibilities = parameter([10**6, 10**7])
    imgsize = parameter([1024])

    @run_after('setup')
    def filter_benchmarks(self):
        self.executable_opts.append(f'--benchmark_filter=PadmmFixtureMPI/'
                                    f'ApplyAlgo{self.algorithm}'
                                    f'/{self.imgsize}/{self.numberOfVisibilities}/')
        self.env_vars['OMP_NUM_THREADS'] = f'{self.threads}'
        self.num_tasks = self.tasks
        self.num_cpus_per_task = self.threads
        self.num_tasks_per_node = 1
