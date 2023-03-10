import os.path as path
import reframe as rfm
import reframe.utility.sanity as sn
import sys

sys.path.append(path.join(path.dirname(__file__), '..', '..'))
from modules.utils import SpackTest


class Ramses_download_inputs(rfm.RunOnlyRegressionTest):

    descr = 'Download Ramses input files'
    executable = 'wget'
    executable_opts = [
        f'http://path/to/inputs'  # noqa: E501
    ]
    local = True

    @run_after('init')
    def link_input_files(self):
        input_dir = path.join(path.dirname(__file__),'data')
        self.executable = 'cp'
        self.executable_opts = [f'-r {input_dir} .']

    @sanity_function
    def validate_download(self):
        return sn.assert_true(path.exists('data'))


class RamsesMPI(SpackTest):

    valid_systems = ['*']
    valid_prog_environs = ['*']

    spack_spec = 'ramses@v1.0.0'
    executable = 'ramses3d'
    executable_opts = ['params.nml']
    sourcesdir = path.join(path.dirname(__file__),'inputs')

    time_limit = '5m'

    reference = {
            '*': {
                'Total elapsed time': (500, None, None, 'seconds'),
                },
            }

    ramses_inputs = fixture(Ramses_download_inputs, scope='session')

    @run_before('compile')
    def setup_build_system(self):
        self.spack_spec = self.spack_spec
        self.build_system.specs = [self.spack_spec]

    @run_before('run')
    def link_input_files(self):
        input_dir = path.join(f'{self.ramses_inputs.stagedir}','data')
        self.prerun_cmds = [f'cp -r {input_dir} {self.stagedir}']

    @sanity_function
    def validate_successful_run(self):
        return sn.assert_found(r'Run completed', self.stdout)

    @performance_function('seconds', perf_key='Total elapsed time')
    def extract_elapsed_time(self):
        return sn.extractsingle(r'Total elapsed time:\s+(\S+)\s', self.stdout, 1, float)


@rfm.simple_test
class RamsesMPI_strong(RamsesMPI):

    tags = {"strong"}
    num_nodes = parameter(2**i for i in range(0,5))

    @run_after('setup')
    def set_job_script_variables(self):

        self.core_count_1_node = self.current_partition.processor.num_cpus // min(1, self.current_partition.processor.num_cpus_per_core)

        self.num_tasks = self.num_nodes * self.core_count_1_node
        self.num_tasks_per_node = self.core_count_1_node    #We are using the full node with MPI tasks.
        self.descr = ('Strong Scaling Ramses on '+ str(self.num_nodes) + ' node/s')


@rfm.simple_test
class RamsesMPI_weak(RamsesMPI):

    tags = {"weak"}
    num_nodes = parameter(2**i for i in range(0,4))

    @run_after('setup')
    def set_job_script_variables(self):

        self.core_count_1_node = self.current_partition.processor.num_cpus // min(1, self.current_partition.processor.num_cpus_per_core)

        self.num_tasks = self.num_nodes * self.core_count_1_node
        self.num_tasks_per_node = self.core_count_1_node
        self.descr = ('Weak Scaling Ramses on '+str(self.num_nodes)+ ' node/s')
        self.executable_opts = ['params'+str(self.num_nodes)+'_weak.nml']
