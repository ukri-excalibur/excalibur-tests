import os.path as path
import reframe as rfm
import reframe.core.runtime as rt
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest


def threads_per_part():
    for p in rt.runtime().system.partitions:
        nthr = 1
        while nthr < p.processor.num_cores:
            yield (p.fullname, nthr)
            nthr <<= 1
        yield (p.fullname, p.processor.num_cores)


class SphngBase(SpackTest):

    descr = 'Base class for Sphng'
    valid_systems = ['-gpu']
    valid_prog_environs = ['default']
    time_limit = '0d0h30m0s'
    exclusive_access = True
    spack_spec = 'sphng@v1.0.0%intel'
    executable = 'sph_tree_rk_gradh'

    num_tasks = required
    num_tasks_per_node = required
    num_cpus_per_task = required

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


class SphngBase_ifile(SphngBase):

    prerun_cmds = ['rm -rf fort* TEST* notify ifile sphng_setup.o']
    executable_opts = ['initial ifile < setup.txt &> sphng_setup.o']

    @sanity_function
    def validate_ifile_generation(self):
        return sn.assert_true(path.exists('ifile'))


class SphngBase_evolution(SphngBase):

    executable_opts = ['evolution ifile']
    postrun_cmds = ['cat test01']

    reference = {
        'dial:slurm-local': {
            'Total elapsed time': (10, None, None, 'minutes'),
            },
        }

    @sanity_function
    def validate_successful_run(self):
        return sn.assert_found(r'ended on', self.stdout)

    @performance_function('minutes', perf_key='Total elapsed time')
    def extract_elapsed_time(self):
        return sn.extractsingle(r'cpu time used for this run :\s+(\S+)\s', self.stdout, 1, float)


class Sphng_Single_Node_ifile(SphngBase_ifile):

    mpi_tasks = parameter(threads_per_part(), fmt=lambda x: x[1])

    @run_after('init')
    def setup_thread_config(self):
        self.valid_systems = [self.mpi_tasks[0]]

    @run_after('setup')
    def set_env_variables(self):

        self.core_count_1_node = self.current_partition.processor.num_cpus // min(1, self.current_partition.processor.num_cpus_per_core)
        self.num_tasks = self.num_tasks_per_node = int(self.mpi_tasks[1])
        self.thread_count = int(self.core_count_1_node/self.num_tasks_per_node)
        self.num_cpus_per_task = self.thread_count

        self.descr = ('Running Sphng (Ifile) on ' +
                      ' single node with ' +
                      str(self.num_tasks_per_node) + ' tasks per node and ' +
                      str(self.num_cpus_per_task) +  ' threads per task')

        self.env_vars['NUM_TASKS_PER_NODE'] = self.num_tasks_per_node
        self.env_vars['OMP_NUM_THREADS'] = self.num_cpus_per_task
        self.set_common_env_variables()


@rfm.simple_test
class Sphng_Single_Node_evolution(SphngBase_evolution):

    descr = 'sphng test: single node'
    tags = {'single-node'}
    Ifile_fixture = fixture(Sphng_Single_Node_ifile)

    @run_after('init')
    def setup_thread_config(self):
        self.valid_systems = [self.Ifile_fixture.mpi_tasks[0]]

    @run_after('setup')
    def set_sourcedir_and_job_params(self):

        self.num_tasks = self.num_tasks_per_node = self.Ifile_fixture.num_tasks
        self.thread_count = self.Ifile_fixture.thread_count
        self.num_cpus_per_task = self.thread_count

        self.descr = ('Running Sphng (Evolution) on ' +
                      ' single node with ' +
                      str(self.num_tasks_per_node) + ' tasks per node and ' +
                      str(self.num_cpus_per_task) +  ' threads per task')

        self.env_vars['NUM_TASKS_PER_NODE'] = self.num_tasks_per_node
        self.env_vars['OMP_NUM_THREADS'] = self.num_cpus_per_task
        self.set_common_env_variables()

        self.sourcesdir = path.join(self.Ifile_fixture.stagedir,'')


class Sphng_Strong_Scaling_ifile(SphngBase_ifile):

    num_nodes = parameter(2**i for i in range(0,5))

    @run_after('setup')
    def set_env_variables(self):

        self.core_count_1_node = self.current_partition.processor.num_cpus // min(1, self.current_partition.processor.num_cpus_per_core)
        self.num_tasks = 16 # hard coded because this gave the best performance.
        self.num_tasks_per_node = int(self.num_tasks/self.num_nodes)
        self.thread_count = int(self.core_count_1_node/self.num_tasks_per_node)
        self.num_cpus_per_task = self.thread_count

        self.descr = ('Running Sphng (Ifile) on ' +
                      str(self.num_nodes) + ' node(s) with ' +
                      str(self.num_tasks_per_node) + ' tasks per node and ' +
                      str(self.num_cpus_per_task) +  ' threads per task')

        self.env_vars['NUM_TASKS_PER_NODE'] = self.num_tasks_per_node
        self.env_vars['OMP_NUM_THREADS'] = self.num_cpus_per_task
        self.set_common_env_variables()


@rfm.simple_test
class Sphng_Strong_Scaling_evolution(SphngBase_evolution):

    descr = 'sphng test: strong scaling'
    tags = {'strong'}
    Ifile_fixture = fixture(Sphng_Strong_Scaling_ifile)

    @run_after('setup')
    def set_sourcedir_and_job_params(self):

        self.num_tasks = self.Ifile_fixture.num_tasks
        self.num_tasks_per_node = self.Ifile_fixture.num_tasks_per_node
        self.thread_count = self.Ifile_fixture.thread_count
        self.num_cpus_per_task = self.thread_count

        self.descr = ('Running Sphng (Evolution) on ' +
                      str(self.Ifile_fixture.num_nodes) + ' node(s) with ' +
                      str(self.num_tasks_per_node) + ' tasks per node and ' +
                      str(self.num_cpus_per_task) +  ' threads per task')

        self.env_vars['NUM_TASKS_PER_NODE'] = self.num_tasks_per_node
        self.env_vars['OMP_NUM_THREADS'] = self.num_cpus_per_task
        self.set_common_env_variables()

        self.sourcesdir = path.join(self.Ifile_fixture.stagedir,'')


class Sphng_Weak_Scaling_ifile(SphngBase_ifile):

    num_nodes = parameter(2**i for i in range(0,5))

    @run_after('setup')
    def set_env_variables(self):

        self.core_count_1_node = self.current_partition.processor.num_cpus // min(1, self.current_partition.processor.num_cpus_per_core)
        self.num_tasks = 16 # hard coded because this gave the best performance.
        self.num_tasks_per_node = int(self.num_tasks/self.num_nodes)
        self.thread_count = int(self.core_count_1_node/self.num_tasks_per_node)
        self.num_cpus_per_task = self.thread_count

        self.descr = ('Running Sphng (Ifile) on ' +
                      str(self.num_nodes) + ' node(s) with ' +
                      str(self.num_tasks_per_node) + ' tasks per node and ' +
                      str(self.num_cpus_per_task) +  ' threads per task')

        self.env_vars['NUM_TASKS_PER_NODE'] = self.num_tasks_per_node
        self.env_vars['OMP_NUM_THREADS'] = self.num_cpus_per_task
        self.set_common_env_variables()

        self.prerun_cmds = ['cp weak_n' + str(self.num_nodes) +'/inspho .', 'cp weak_n'+ str(self.num_nodes) + '/setup.txt .']


@rfm.simple_test
class Sphng_Weak_Scaling_evolution(SphngBase_evolution):

    descr = 'sphng test: weak scaling'
    tags = {'weak'}
    Ifile_fixture = fixture(Sphng_Weak_Scaling_ifile)

    @run_after('setup')
    def set_sourcedir_and_job_params(self):

        self.num_tasks = self.Ifile_fixture.num_tasks
        self.num_tasks_per_node = self.Ifile_fixture.num_tasks_per_node
        self.thread_count = self.Ifile_fixture.thread_count
        self.num_cpus_per_task = self.thread_count

        self.descr = ('Running Sphng (Evolution) on ' +
                      str(self.Ifile_fixture.num_nodes) + ' node(s) with ' +
                      str(self.num_tasks_per_node) + ' tasks per node and ' +
                      str(self.num_cpus_per_task) +  ' threads per task')

        self.env_vars['NUM_TASKS_PER_NODE'] = self.num_tasks_per_node
        self.env_vars['OMP_NUM_THREADS'] = self.num_cpus_per_task
        self.set_common_env_variables()

        self.sourcesdir = path.join(self.Ifile_fixture.stagedir,'')
