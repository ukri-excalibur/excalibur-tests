import reframe as rfm
import reframe.utility.sanity as sn

#------------------------------------------------------------------------------------------------------------------------------------
# Base class for Ramses.
# Also defines the sanity test.
#------------------------------------------------------------------------------------------------------------------------------------
class RamsesMPI(rfm.RunOnlyRegressionTest):
    
    def __init__(self):

        self.time_limit = '0d0h10m0s'
        self.exclusive_access=True
        self.valid_systems = ['*']
        self.valid_prog_environs = ['*']
        self.executable = './ramses3d'
        self.executable_opts = ['params.nml']
        reference = {
        'dial:slurm-local': {
            'Total elapsed time:':  (500, None, None, 'seconds'),
                            }
                    }

    @run_before('sanity')
    def run_complete_pattern(self):
        self.pattern = r'Run completed'
        self.sanity_patterns = sn.assert_found(self.pattern, self.stdout)


    @run_before('performance')
    def runtime_extract_pattern(self):
        self.perf_patterns = {'Total elapsed time': sn.extractsingle(r'Total elapsed time:\s+(\S+)\s', self.stdout, 1, float)}

#------------------------------------------------------------------------------------------------------------------------------------
# End of base class.
#------------------------------------------------------------------------------------------------------------------------------------




#------------------------------------------------------------------------------------------------------------------------------------
# Strong scaling test.
#------------------------------------------------------------------------------------------------------------------------------------
@rfm.simple_test
class RamsesMPI_strong(RamsesMPI):

    tags = {"Strong"}
    num_nodes = parameter(2**i for i in range(0,5))
    
    @run_after('setup')
    def set_job_script_variables(self):

        if self.current_partition.processor.num_cpus_per_core > 1:
            self.core_count_1_node = int(self.current_partition.processor.num_cpus/self.current_partition.processor.num_cpus_per_core)
        else:    
            self.core_count_1_node = self.current_partition.processor.num_cpus 
        
        self.num_tasks = self.num_nodes * self.core_count_1_node
        self.num_tasks_per_node = self.core_count_1_node    #We are using the full node with MPI tasks.
        self.descr = ('Strong Scaling Ramses on '+ str(self.num_nodes) + ' node/s')

#------------------------------------------------------------------------------------------------------------------------------------
# End of strong scaling test.
#------------------------------------------------------------------------------------------------------------------------------------




#------------------------------------------------------------------------------------------------------------------------------------
# Weak scaling tests.
#------------------------------------------------------------------------------------------------------------------------------------
@rfm.simple_test
class RamsesMPI_weak(RamsesMPI):
    
    tags = {"Weak"}
    num_nodes = parameter(2**i for i in range(0,4))

    @run_after('setup')
    def set_job_script_variables(self):

        if self.current_partition.processor.num_cpus_per_core > 1:
            self.core_count_1_node = int(self.current_partition.processor.num_cpus/self.current_partition.processor.num_cpus_per_core)
        else:    
            self.core_count_1_node = self.current_partition.processor.num_cpus 
        
        self.num_tasks = self.num_nodes * self.core_count_1_node
        self.num_tasks_per_node = self.core_count_1_node
        self.descr = ('Weak Scaling Ramses on '+str(self.num_nodes)+ ' node/s')
        self.executable_opts = ['params'+str(self.num_nodes)+'_weak.nml']

#------------------------------------------------------------------------------------------------------------------------------------
# End of weak scaling tests.
#------------------------------------------------------------------------------------------------------------------------------------

