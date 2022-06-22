import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps

#--------------------------------------------------------------------------
# Define base class for Trove.
# This class will be used for all 3 cases namely 12N, 14N and 16N.
#--------------------------------------------------------------------------
class Trove(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Base class for Trove'
        self.time_limit = '0d2h0m0s'
        self.exclusive_access=True
        self.valid_systems = ['*']
        self.valid_prog_environs = ['*']
        self.executable = './j-trove.x'
        self.postrun_cmds = ['tail -n 100 output.txt']

        reference = {
         'dial:slurm-local': {
             'Total elapsed time:':  (5000, None, None, 'seconds'),
                             }
                     }

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

#--------------------------------------------------------------------------
# End of Base class.
#--------------------------------------------------------------------------



#--------------------------------------------------------------------------
# Code to run the benchmark for input file named 12N.
#--------------------------------------------------------------------------
@rfm.simple_test
class TROVE_12N(Trove):

    tags = {"12N"}
    param_value = parameter(i for i in range(0,3))
    num_nodes_current_run =  [1,  2,  4]
    num_mpi_tasks         =  [32, 32, 64]

    def __init__(self):
        super().__init__()
        self.executable_opts = ['N12.inp > output.txt']

    @run_after('setup')
    def set_job_script_variables(self):

        if self.current_partition.processor.num_cpus_per_core > 1:
            self.core_count_1_node = int(self.current_partition.processor.num_cpus/self.current_partition.processor.num_cpus_per_core)
        else:    
            self.core_count_1_node = self.current_partition.processor.num_cpus
        
        self.num_tasks = self.num_mpi_tasks[self.param_value]
        self.num_tasks_per_node = int(self.num_tasks/self.num_nodes_current_run[self.param_value])
        self.descr = ('Running Trove on ' + str(self.num_nodes_current_run[self.param_value]) + ' nodes with ' + str(self.num_tasks_per_node) + ' tasks per node and ' + str(self.num_cpus_per_task) +  ' threads per node')
        self.variables= {
            'OMP_NUM_THREADS':str(int(self.core_count_1_node/self.num_tasks_per_node)),
            'OMP_PLACES':'cores'
        }

#--------------------------------------------------------------------------
# End of code for file named 12N.
#--------------------------------------------------------------------------

#--------------------------------------------------------------------------
# Code to run the benchmark for input file named 14N.
#--------------------------------------------------------------------------
@rfm.simple_test
class TROVE_14N(Trove):

    tags = {"14N"}
    param_value = parameter(i for i in range(0,5))
    num_nodes_current_run = [1,  2,  4,  8,  16]
    num_mpi_tasks         = [64, 32, 64, 64, 32]

    def __init__(self):
        super().__init__()
        self.executable_opts = ['N14.inp > output.txt']

    @run_after('setup')
    def set_job_script_variables(self):

        if self.current_partition.processor.num_cpus_per_core > 1:
            self.core_count_1_node = int(self.current_partition.processor.num_cpus/self.current_partition.processor.num_cpus_per_core)
        else:    
            self.core_count_1_node = self.current_partition.processor.num_cpus    
        
        self.num_tasks = self.num_mpi_tasks[self.param_value]
        self.num_tasks_per_node = int(self.num_tasks/self.num_nodes_current_run[self.param_value])
        self.descr = ('Running Trove on ' + str(self.num_nodes_current_run[self.param_value]) + ' nodes with ' + str(self.num_tasks_per_node) + ' tasks per node and ' + str(self.num_cpus_per_task) +  ' threads per node')
        self.variables= {
            'OMP_NUM_THREADS':str(int(self.core_count_1_node/self.num_tasks_per_node)),
            'OMP_PLACES':'cores'
        }

#--------------------------------------------------------------------------
# End of code for file named 14N.
#--------------------------------------------------------------------------

#--------------------------------------------------------------------------
# Code to run the benchmark for input file named 16N.
#--------------------------------------------------------------------------
@rfm.simple_test
class TROVE_16N(Trove):

    tags = {"16N"}
    param_value = parameter(i for i in range(0,5))
    num_nodes_current_run = [1,  2,  4,  8,   16]
    num_mpi_tasks         = [32, 32, 64, 128, 128]

    def __init__(self):
        super().__init__()
        self.executable_opts = ['N16.inp > output.txt']

    @run_after('setup')
    def set_job_script_variables(self):

        if self.current_partition.processor.num_cpus_per_core > 1:
            self.core_count_1_node = int(self.current_partition.processor.num_cpus/self.current_partition.processor.num_cpus_per_core)
        else:    
            self.core_count_1_node = self.current_partition.processor.num_cpus
        
        self.num_tasks = self.num_mpi_tasks[self.param_value]
        self.num_tasks_per_node = int(self.num_tasks/self.num_nodes_current_run[self.param_value])
        self.descr = ('Running Trove on ' + str(self.num_nodes_current_run[self.param_value]) + ' nodes with ' + str(self.num_tasks_per_node) + ' tasks per node and ' + str(self.num_cpus_per_task) +  ' threads per node')
        self.variables= {
            'OMP_NUM_THREADS':str(int(self.core_count_1_node/self.num_tasks_per_node)),
            'OMP_PLACES':'cores'
        }

#--------------------------------------------------------------------------
# End of code for file named 16N.
#--------------------------------------------------------------------------




