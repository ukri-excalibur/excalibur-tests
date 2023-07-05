import reframe as rfm
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest


class TroveBase(SpackTest):

    descr = 'Base class for Trove'
    valid_systems = ['-gpu']
    valid_prog_environs = ['default']
    time_limit = '0d2h30m0s'
    exclusive_access = True
    spack_spec = 'trove@v1.0.0%intel'
    executable = 'j-trove.x'

    num_tasks = required
    num_tasks_per_node = required
    num_cpus_per_task = required

    reference = {
            'dial:slurm-local': {
                'Total elapsed time': (500, None, None, 'seconds'),
                },
            }

    def set_common_env_variables(self):
        self.env_vars['OMP_PLACES'] = 'cores'

        # pre-requisite IntelMPI's mpirun launcher so far...
        if(self.current_partition.scheduler.registered_name == 'slurm'):
            if(self.num_tasks_per_node <= self.current_partition.processor.num_cpus_per_socket):
                self.env_vars['I_MPI_PIN_RESPECT_CPUSET'] = '0'
        elif(self.current_partition.scheduler.registered_name == 'torque'):
            self.env_vars['I_MPI_JOB_RESPECT_PROCESS_PLACEMENT'] = 'off'
            self.executable = '-perhost $NUM_TASKS_PER_NODE ' + self.executable

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = [self.spack_spec]

    @sanity_function
    def validate_successful_run(self):
        return sn.assert_found(r'End of TROVE', self.stdout)

    @performance_function('seconds', perf_key='Total elapsed time')
    def extract_elapsed_time(self):
        return sn.extractsingle(r'TROVE\s{30}\s+(\S+)\s+(\S+)', self.stdout, 2, float)


@rfm.simple_test
class TROVE_12N(TroveBase):

    descr = 'trove test: 12N'
    tags = {'12N'}
    executable_opts = ['N12.inp']

    param_value = parameter(i for i in range(0,3))
    num_nodes_current_run =  [1,  2,  4]
    num_mpi_tasks         =  [32, 32, 64]

    @run_after('setup')
    def set_job_script_variables(self):

        self.core_count_1_node = self.current_partition.processor.num_cpus // min(1, self.current_partition.processor.num_cpus_per_core)
        self.num_tasks = self.num_mpi_tasks[self.param_value]
        self.num_tasks_per_node = int(self.num_tasks/self.num_nodes_current_run[self.param_value])
        self.num_cpus_per_task = int(self.core_count_1_node/self.num_tasks_per_node)

        self.descr = ('Running Trove on ' +
                      str(self.num_nodes_current_run[self.param_value]) + ' node(s) with ' +
                      str(self.num_tasks_per_node) + ' tasks per node and ' +
                      str(self.num_cpus_per_task) +  ' threads per task')

        self.env_vars['NUM_TASKS_PER_NODE'] = self.num_tasks_per_node
        self.env_vars['OMP_NUM_THREADS'] = self.num_cpus_per_task
        self.set_common_env_variables()


@rfm.simple_test
class TROVE_14N(TroveBase):

    descr = 'trove test: 14N'
    tags = {'14N'}
    executable_opts = ['N14.inp']

    param_value = parameter(i for i in range(0,5))
    num_nodes_current_run = [1,  2,  4,  8,  16]
    num_mpi_tasks         = [64, 32, 64, 64, 32]

    @run_after('setup')
    def set_job_script_variables(self):

        self.core_count_1_node = self.current_partition.processor.num_cpus // min(1, self.current_partition.processor.num_cpus_per_core)
        self.num_tasks = self.num_mpi_tasks[self.param_value]
        self.num_tasks_per_node = int(self.num_tasks/self.num_nodes_current_run[self.param_value])
        self.num_cpus_per_task = int(self.core_count_1_node/self.num_tasks_per_node)

        self.descr = ('Running Trove on ' +
                      str(self.num_nodes_current_run[self.param_value]) + ' node(s) with ' +
                      str(self.num_tasks_per_node) + ' tasks per node and ' +
                      str(self.num_cpus_per_task) +  ' threads per task')

        self.env_vars['NUM_TASKS_PER_NODE'] = self.num_tasks_per_node
        self.env_vars['OMP_NUM_THREADS'] = self.num_cpus_per_task
        self.set_common_env_variables()


@rfm.simple_test
class TROVE_16N(TroveBase):

    descr = 'trove test: 16N'
    tags = {'16N'}
    executable_opts = ['N16.inp']

    param_value = parameter(i for i in range(0,5))
    num_nodes_current_run = [1,  2,  4,  8,   16]
    num_mpi_tasks         = [32, 32, 64, 128, 128]

    @run_after('setup')
    def set_job_script_variables(self):

        self.core_count_1_node = self.current_partition.processor.num_cpus // min(1, self.current_partition.processor.num_cpus_per_core)
        self.num_tasks = int(self.num_mpi_tasks[self.param_value])
        self.num_tasks_per_node = int(self.num_tasks/self.num_nodes_current_run[self.param_value])
        self.num_cpus_per_task = int(self.core_count_1_node/self.num_tasks_per_node)

        self.descr = ('Running Trove on ' +
                      str(self.num_nodes_current_run[self.param_value]) + ' node(s) with ' +
                      str(self.num_tasks_per_node) + ' tasks per node and ' +
                      str(self.num_cpus_per_task) +  ' threads per task')

        self.env_vars['NUM_TASKS_PER_NODE'] = self.num_tasks_per_node
        self.env_vars['OMP_NUM_THREADS'] = self.num_cpus_per_task
        self.set_common_env_variables()
