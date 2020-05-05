import reframe as rfm
import reframe.utility.sanity as sn

@rfm.simple_test
class IMB_MPI1Test(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Test of using reframe to run IMB-MPI1'
        self.valid_systems = ['sausage-newslurm:compute']
        self.valid_prog_environs = ['gnu8-openmpi3']
        self.sourcedir = None
        self.modules = ['imb']
        self.executable = 'IMB-MPI1' # mpirun --mca btl_base_warn_component_unused 0 IMB-MPI1 uniband biband
        self.executable_opts = ['uniband', 'biband']
        self.sanity_patterns = sn.assert_found('# Benchmarking Uniband', self.stdout)
        self.num_tasks = 2
        self.num_tasks_per_node = 1
        