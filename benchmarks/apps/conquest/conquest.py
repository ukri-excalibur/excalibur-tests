# Import modules from reframe and excalibur-tests
import reframe as rfm
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest

class ConquestBaseBenchmark(SpackTest):

    # Run configuration
    ## Mandatory ReFrame setup
    valid_systems = ['*']
    valid_prog_environs = ['default']

    ## Executable
    executable = 'Conquest'
    executable_opts = ['']

    ## Scheduler options
    time_limit = '30m'

    # Build configuration
    spack_spec = 'conquest@develop +openmp'

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

    input_dir = "$(dirname $(which Conquest))/../benchmarks/K222_G200"

    prerun_cmds.append(f"cp {input_dir}/coords.dat .")
    prerun_cmds.append(f"cp {input_dir}/Conquest_input .")
    prerun_cmds.append(f"cp {input_dir}/Si.ion .")

@rfm.simple_test
class Water64(ConquestBaseBenchmark):

    tags = {"water64"}
    num_tasks = 8
    num_cpus_per_task = 4

    input_dir = "$(dirname $(which Conquest))/../benchmarks/water_64mols"

    prerun_cmds.append(f"cp {input_dir}/Conquest_input .")
    prerun_cmds.append(f"cp {input_dir}/H20_coord.in .")
    prerun_cmds.append(f"cp {input_dir}/H_SZ.ion .")
    prerun_cmds.append(f"cp {input_dir}/H_SZP.ion .")
    prerun_cmds.append(f"cp {input_dir}/O_SZ.ion .")
    prerun_cmds.append(f"cp {input_dir}/O_SZP.ion .")

@rfm.simple_test
class SiWeakScaling(ConquestBaseBenchmark):

    tags = {"si_weakscaling"}
    num_threads = parameter([1,2,4,8])
    num_cores = parameter([8,16,32,64,128,256,512])

    def __init__(self):
        input_files = {
            8: "si_222.xtl",
            16: "si_422.xtl",
            32: "si_442.xtl",
            64: "si_444.xtl",
            128: "si_844.xtl",
            256: "si_884.xtl",
            512: "si_888.xtl" }
        input_dir = "$(dirname $(which Conquest))/../benchmarks/matrix_multiply"

        self.num_tasks = int(self.num_cores / self.num_threads)
        self.num_cpus_per_task = self.num_threads

        self.prerun_cmds.append(f"cp {input_dir}/{input_files[self.num_cores]} ./coords.dat")
        self.prerun_cmds.append(f"cp {input_dir}/Conquest_input .")
        self.prerun_cmds.append(f"cp {input_dir}/Si.ion .")
