import reframe as rfm
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest


class Trove(SpackTest):

    descr = 'Base class for Trove'
    valid_systems = ['*']
    valid_prog_environs = ['*']
    spack_spec = 'trove@v1.0.0'
    executable = 'j-trove.x'
    postrun_cmds = ['tail -n 100 output.txt']
    time_limit = '0d2h0m0s'
    exclusive_access = True

    reference = {
            'dial:slurm-local': {
                'Total elapsed time': (500, None, None, 'seconds'),
                },
            }

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = [self.spack_spec]

    @run_before('sanity')
    def run_complete_pattern(self):
        self.pattern = r'End of TROVE'
        self.sanity_patterns = sn.assert_found(self.pattern, 'output.txt')

    @performance_function('seconds')
    def get_elapsed_time(self):
        return sn.extractsingle(r'TROVE\s+(\S+)\s+(\S+)', self.stdout, 2, float)

    @run_before('performance')
    def runtime_extract_pattern(self):
        self.perf_variables = {
                'Total elapsed time':self.get_elapsed_time()
                }


@rfm.simple_test
class TROVE_12N(Trove):

    descr = 'trove test: 12N'
    tags = {'12N'}
    executable_opts = ['N12.inp > output.txt']

    param_value = parameter(i for i in range(0,3))
    num_nodes_current_run =  [1,  2,  4]
    num_mpi_tasks         =  [32, 32, 64]

    @run_after('setup')
    def set_job_script_variables(self):

        self.core_count_1_node = self.current_partition.processor.num_cpus // min(1, self.current_partition.processor.num_cpus_per_core)

        self.num_tasks = self.num_mpi_tasks[self.param_value]
        self.num_tasks_per_node = int(self.num_tasks/self.num_nodes_current_run[self.param_value])
        self.descr = ('Running Trove on ' + str(self.num_nodes_current_run[self.param_value]) + ' nodes with ' + str(self.num_tasks_per_node) + ' tasks per node and ' + str(self.num_cpus_per_task) +  ' threads per node')
        self.thread_count = str(int(self.core_count_1_node/self.num_tasks_per_node))
        self.env_vars['OMP_NUM_THREADS'] = self.thread_count
        self.env_vars['OMP_PLACES'] = 'cores'


@rfm.simple_test
class TROVE_14N(Trove):

    descr = 'trove test: 14N'
    tags = {'14N'}
    executable_opts = ['N14.inp > output.txt']

    param_value = parameter(i for i in range(0,5))
    num_nodes_current_run = [1,  2,  4,  8,  16]
    num_mpi_tasks         = [64, 32, 64, 64, 32]

    @run_after('setup')
    def set_job_script_variables(self):

        self.core_count_1_node = self.current_partition.processor.num_cpus // min(1, self.current_partition.processor.num_cpus_per_core)

        self.num_tasks = self.num_mpi_tasks[self.param_value]
        self.num_tasks_per_node = int(self.num_tasks/self.num_nodes_current_run[self.param_value])
        self.descr = ('Running Trove on ' + str(self.num_nodes_current_run[self.param_value]) + ' nodes with ' + str(self.num_tasks_per_node) + ' tasks per node and ' + str(self.num_cpus_per_task) +  ' threads per node')
        self.thread_count = str(int(self.core_count_1_node/self.num_tasks_per_node))
        self.env_vars['OMP_NUM_THREADS'] = self.thread_count
        self.env_vars['OMP_PLACES'] = 'cores'


@rfm.simple_test
class TROVE_16N(Trove):

    descr = 'trove test: 16N'
    tags = {'16N'}
    executable_opts = ['N16.inp > output.txt']

    param_value = parameter(i for i in range(0,5))
    num_nodes_current_run = [1,  2,  4,  8,   16]
    num_mpi_tasks         = [32, 32, 64, 128, 128]

    @run_after('setup')
    def set_job_script_variables(self):

        self.core_count_1_node = self.current_partition.processor.num_cpus // min(1, self.current_partition.processor.num_cpus_per_core)

        self.num_tasks = self.num_mpi_tasks[self.param_value]
        self.num_tasks_per_node = int(self.num_tasks/self.num_nodes_current_run[self.param_value])
        self.descr = ('Running Trove on ' + str(self.num_nodes_current_run[self.param_value]) + ' nodes with ' + str(self.num_tasks_per_node) + ' tasks per node and ' + str(self.num_cpus_per_task) +  ' threads per node')
        self.thread_count = str(int(self.core_count_1_node/self.num_tasks_per_node))
        self.env_vars['OMP_NUM_THREADS'] = self.thread_count
        self.env_vars['OMP_PLACES'] = 'cores'
