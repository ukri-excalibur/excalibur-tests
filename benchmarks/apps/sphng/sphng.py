import os.path as path
import reframe as rfm
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest


class SphngBase(SpackTest):

    descr = 'Base class for Sphng'
    valid_systems = ['*']
    valid_prog_environs = ['*']
    spack_spec = 'sphng@v1.0.0'
    executable = 'sph_tree_rk_gradh'
    time_limit = '0d0h30m0s'

    num_tasks = required
    num_tasks_per_node = required
    num_cpus_per_task = required

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = [self.spack_spec]


class SphngBase_ifile(SphngBase):

    prerun_cmds = ['rm -rf fort* TEST* notify ifile sphng_setup.o']
    executable_opts = ['initial ifile < ./setup.txt &> sphng_setup.o']

    @sanity_function
    def validate_ifile_generation(self):
        return sn.assert_true(path.exists('ifile'))


class SphngBase_evolution(SphngBase):

    executable_opts = ['evolution ifile']

    reference = {
        'dial:slurm-local': {
            'Total elapsed time': (10, None, None, 'minutes'),
            },
        }

    @run_before('sanity')
    def run_complete_pattern(self):
        self.pattern = r'ended on'
        self.sanity_patterns = sn.assert_found(self.pattern, 'test01')

    @performance_function('minutes')
    def get_elapsed_time(self):
        return sn.extractsingle(r'cpu time used for this run :\s+(\S+)\s', 'test01', 1, float)

    @run_before('performance')
    def runtime_extract_pattern(self):
        self.perf_variables = {
                'Total elapsed time':self.get_elapsed_time()
                }


class Sphng_Single_Node_ifile(SphngBase_ifile):

    mpi_tasks = parameter(2**i for i in range(0,8))

    @run_after('setup')
    def set_env_variables(self):

        self.core_count_1_node = self.current_partition.processor.num_cpus // min(1, self.current_partition.processor.num_cpus_per_core)
        self.num_tasks = self.mpi_tasks
        self.num_tasks_per_node = self.mpi_tasks
        self.thread_count = int(self.core_count_1_node/self.num_tasks_per_node)
        self.set_var_default('num_cpus_per_task', self.thread_count)

        self.descr = ('Running Sphng (Ifile) on ' + str(self.num_tasks_per_node) +' tasks and ' + \
                       str(self.thread_count) +  ' threads per node')

        self.env_vars['NUM_TASKS_PER_NODE'] = self.num_tasks_per_node
        self.env_vars['OMP_NUM_THREADS'] = self.thread_count
        self.env_vars['OMP_PLACES'] = 'cores'


@rfm.simple_test
class Sphng_Single_Node_evolution(SphngBase_evolution):

    descr = 'sphng test: single node'
    tags = {'single-node'}
    Ifile_fixture = fixture(Sphng_Single_Node_ifile)

    @run_after('setup')
    def set_sourcedir_and_job_params(self):

        self.num_tasks = self.Ifile_fixture.mpi_tasks
        self.num_tasks_per_node = self.Ifile_fixture.mpi_tasks
        self.thread_count = self.Ifile_fixture.thread_count
        self.set_var_default('num_cpus_per_task', self.thread_count)

        self.descr = ('Running Sphng (Evolution) on ' + str(self.num_tasks_per_node) +' tasks and ' + \
                       str(self.thread_count) +  ' threads per node')

        self.env_vars['NUM_TASKS_PER_NODE'] = self.num_tasks_per_node
        self.env_vars['OMP_NUM_THREADS'] = self.thread_count
        self.env_vars['OMP_PLACES'] = 'cores'

        self.sourcesdir = path.join(self.Ifile_fixture.stagedir,'')


class Sphng_Strong_Scaling_ifile(SphngBase_ifile):

    num_nodes = parameter(2**i for i in range(0,5))

    @run_after('setup')
    def set_env_variables(self):

        self.core_count_1_node = self.current_partition.processor.num_cpus // min(1, self.current_partition.processor.num_cpus_per_core)
        self.num_tasks = 16 # hard coded because this gave the best performance.
        self.num_tasks_per_node = int(self.num_tasks/self.num_nodes)
        self.thread_count = int(self.core_count_1_node/self.num_tasks_per_node)
        self.set_var_default('num_cpus_per_task', self.thread_count)

        self.descr = ('Running Sphng (Ifile) on ' + str(self.num_nodes) + ' nodes with ' + \
                       str(self.num_tasks_per_node) + ' tasks per node and ' + str(self.thread_count) + ' threads per node')

        self.env_vars['NUM_TASKS_PER_NODE'] = self.num_tasks_per_node
        self.env_vars['OMP_NUM_THREADS'] = self.thread_count
        self.env_vars['OMP_PLACES'] = 'cores'


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
        self.set_var_default('num_cpus_per_task', self.thread_count)

        self.descr = ('Running Sphng (Evolution) on ' + str(self.Ifile_fixture.num_nodes) + ' nodes with ' +\
                       str(self.num_tasks_per_node) + ' tasks per node and ' + str(self.thread_count) +  ' threads per node')

        self.env_vars['NUM_TASKS_PER_NODE'] = self.num_tasks_per_node
        self.env_vars['OMP_NUM_THREADS'] = self.thread_count
        self.env_vars['OMP_PLACES'] = 'cores'

        self.sourcesdir = path.join(self.Ifile_fixture.stagedir,'')


class Sphng_Weak_Scaling_ifile(SphngBase_ifile):

    num_nodes = parameter(2**i for i in range(0,5))

    @run_after('setup')
    def set_env_variables(self):

        self.core_count_1_node = self.current_partition.processor.num_cpus // min(1, self.current_partition.processor.num_cpus_per_core)
        self.num_tasks = 16 # hard coded because this gave the best performance.
        self.num_tasks_per_node = int(self.num_tasks/self.num_nodes)
        self.thread_count = int(self.core_count_1_node/self.num_tasks_per_node)
        self.set_var_default('num_cpus_per_task', self.thread_count)

        self.descr = ('Running Sphng (Ifile) on ' + str(self.num_nodes) + ' nodes with ' + \
                       str(self.num_tasks_per_node) + ' tasks per node and ' + str(self.thread_count) +  ' threads per node')

        self.env_vars['NUM_TASKS_PER_NODE'] = self.num_tasks_per_node
        self.env_vars['OMP_NUM_THREADS'] = self.thread_count
        self.env_vars['OMP_PLACES'] = 'cores'

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
        self.set_var_default('num_cpus_per_task', self.thread_count)

        self.descr = ('Running Sphng (Evolution) on ' + str(self.Ifile_fixture.num_nodes) + ' nodes with ' +\
                       str(self.num_tasks_per_node) + ' tasks per node and ' + str(self.thread_count) +  ' threads per node')

        self.env_vars['NUM_TASKS_PER_NODE'] = self.num_tasks_per_node
        self.env_vars['OMP_NUM_THREADS'] = self.thread_count
        self.env_vars['OMP_PLACES'] = 'cores'

        self.sourcesdir = path.join(self.Ifile_fixture.stagedir,'')
