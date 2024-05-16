# Import modules from reframe and excalibur-tests
import reframe as rfm
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest

class ConquestBaseBenchmark(rfm.RunOnlyRegressionTest):

    # Run configuration
    ## Mandatory ReFrame setup
    valid_systems = ['*']
    valid_prog_environs = ['default']

    ## Executable
    executable = 'Conquest'
    executable_opts = ['']

    ## Scheduler options
    time_limit = '30m'

    input_dir = variable(str, value='foo')

    # Build configuration
    # spack_spec = 'conquest@develop +openmp'

    @run_after('setup')
    def setup_variables(self):
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'

    @sanity_function
    def validate_solution(self):
        return sn.assert_found(r'This job was run on', self.stdout)

    @performance_function('s', perf_key='Runtime')
    def extract_copy_perf(self):
        return sn.extractsingle(r'Total run time was:\s+(\S+)\s+seconds', self.stdout, 1, float)

@rfm.simple_test
class Si64(ConquestBaseBenchmark):

    tags = {"silicon64"}
    num_tasks = 8
    num_cpus_per_task = 1

    @run_before('run')
    def get_input(self):
        self.prerun_cmds.append(f"cp {self.input_dir}/K222_G200/coords.dat .")
        self.prerun_cmds.append(f"cp {self.input_dir}/K222_G200/Conquest_input .")
        self.prerun_cmds.append(f"cp {self.input_dir}/K222_G200/Si.ion .")

@rfm.simple_test
class Water64(ConquestBaseBenchmark):

    tags = {"water64"}
    num_tasks = 8
    num_cpus_per_task = 4

    @run_before('run')
    def get_input(self):
        self.prerun_cmds.append(f"cp {self.input_dir}/water_64mols/Conquest_input .")
        self.prerun_cmds.append(f"cp {self.input_dir}/water_64mols/H2O_coord.in .")
        self.prerun_cmds.append(f"cp {self.input_dir}/water_64mols/H_SZ.ion .")
        self.prerun_cmds.append(f"cp {self.input_dir}/water_64mols/H_SZP.ion .")
        self.prerun_cmds.append(f"cp {self.input_dir}/water_64mols/O_SZ.ion .")
        self.prerun_cmds.append(f"cp {self.input_dir}/water_64mols/O_SZP.ion .")

@rfm.simple_test
class SiWeakScaling(ConquestBaseBenchmark):

    tags = {"si_weakscaling"}
    num_threads = parameter([1,2,4,8])
    num_cores = parameter([8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768])
    #num_cores = parameter([8])
    num_atoms_per_core = parameter([8])

    @run_after('setup')
    def setup_variables(self):

        input_files = {
            2**6: "si_222.xtl",
            2**7: "si_422.xtl",
            2**8: "si_442.xtl",
            2**9:  "si_444.xtl",
            2**10: "si_844.xtl",
            2**11: "si_884.xtl",
            2**12:"si_888.xtl",
            2**13: "si_1688.xtl",
            2**14: "si_16168.xtl",
            2**15: "si_161616.xtl",
            2**16: "si_321616.xtl",
            2**17: "si_323216.xtl",
            2**18: "si_323232.xtl"}

        self.num_tasks = max(1, self.num_cores // self.num_threads)
        self.num_cpus_per_task = self.num_threads
        self.num_tasks_per_node = max(1, min(self.num_tasks, self.current_partition.processor.num_cpus // self.num_threads))
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'

        self.prerun_cmds.append(f"cp {self.input_dir}/matrix_multiply/{input_files[self.num_cores*self.num_atoms_per_core]} ./coords.dat")
        self.prerun_cmds.append(f"cp {self.input_dir}/matrix_multiply/Conquest_input .")
        self.prerun_cmds.append(f"cp {self.input_dir}/matrix_multiply/Si.ion .")

        self.time_limit = "2h"

    # Performance tuning by passing system specific scheduler options
    @run_before('run')
    def set_cpu_binding(self):
        if self.current_system.name == 'archer2':
            self.job.launcher.options = ['--distribution=block:block --hint=nomultithread']
