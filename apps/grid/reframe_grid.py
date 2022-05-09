"""
ReFrame benchmark for GIRD: https://github.com/paboyle/Grid

Assumes a GRID install is present on the system. Developed from
https://github.com/DiRAC-HPC/es-benchmarking-public

WARNING:
The code is Hybrid OpenMP + MPI with NUMA socket aware optimisations.
The relevant options can make big changes to delivered performance.
"""
import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class GridBenchmark(rfm.RunOnlyRegressionTest):

    valid_systems = ['*']
    valid_prog_environs = ['intel20-mpi']

    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = 20

    executable = 'Benchmark_ITT'
    executable_opts = ['--shm 1024 --shm-hugetlb']
    time_limit = '20m'
    variables = {
        'OMP_NUM_THREADS': f'{num_cpus_per_task}',
    }
    extra_resources = {
        'mpi': {'num_slots': num_tasks * num_cpus_per_task}
    }

    reference = {
        'csd3:icelake': {
            'Performance': (228286, None, None, 'Mflop/s per node')
        },
        '*': {
            'Performance': (150000, None, None, 'Mflop/s per node'),
        }
    }

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found(r'Per Node Summary table',
                                               self.stdout)

    @run_before('performance')
    def set_perf_patterns(self):
        """
        e.g.

        Grid : Message : 380809 ms :  Comparison point  result: 143382.7 Mflop/s per node
        """

        self.perf_patterns = {
            'Performance':
                sn.extractsingle('result: (\S+) Mflop/s per node', self.stdout, 1, float)
                }
