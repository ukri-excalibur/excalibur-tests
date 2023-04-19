import os.path as path
import reframe as rfm
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest


class PdsyevBase(SpackTest):

    valid_systems = ['*']
    valid_prog_environs = ['*']

    spack_spec = 'trove-pdsyev@v1.0.0'
    executable = 'diag_generic.x'
    executable_opts = ['< gen_n_15K.inp']
    sourcesdir = path.join(path.dirname(__file__),'inputs')

    num_tasks = required
    num_tasks_per_node = required

    time_limit = '4m'

    reference = {
            '*': {
                'diagonlization': (200, None, None, 'seconds'),
                },
            }

    @run_before('compile')
    def setup_build_system(self):
        self.spack_spec = self.spack_spec
        self.build_system.specs = [self.spack_spec]

    @sanity_function
    def validate_successful_run(self):
        return sn.assert_found(r'Diagonalization finished successfully', self.stdout)

    @performance_function('seconds', perf_key='diagonlization')
    def extract_elapsed_time(self):
        return sn.extractsingle(r'Time to diagonalize matrix is \s+(\S+)\s', self.stdout, 1, float)

    @run_after('setup')
    def set_job_script_variables(self):

        proc_info = self.current_partition.processor
        self.set_var_default(
                'num_tasks',
                (proc_info.num_cpus // min(1, proc_info.num_cpus_per_core)) // self.num_threads,
                )
        self.set_var_default(
                'num_tasks_per_node',
                self.num_tasks,
                )
        self.env_vars= {
            'OMP_NUM_THREADS': str(self.num_threads),
            'OMP_PLACES': 'cores',
        }


@rfm.simple_test
class PdsyevSingle(PdsyevBase):

    descr = 'trove-pdsyev test: single node'
    tags = {'single-node'}
    num_threads = parameter(2**i for i in range(0,2))


# @rfm.simple_test
# class PdsyevSingle(PdsyevBase):

#     descr = 'trove-pdsyev test: single node'
#     tags = {'single-node'}
#     num_threads = parameter(2**i for i in range(0,2))
