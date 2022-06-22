import os
import sys
import reframe as rfm
import reframe.utility.sanity as sn
import reframe.utility.udeps as udeps

#------------------------------------------------------------------------------------------------------------------------------------
# Define base class for Sphng.
#------------------------------------------------------------------------------------------------------------------------------------
class SphngBase(rfm.RunOnlyRegressionTest):
    def __init__(self):
        self.descr = 'Base class for Sphng'
        self.time_limit = '0d0h10m0s'
        self.exclusive_access=True
        self.valid_systems = ['*']
        self.valid_prog_environs = ['*']
        self.executable = './sph_tree_rk_gradh'

#------------------------------------------------------------------------------------------------------------------------------------
# End of base class.
#------------------------------------------------------------------------------------------------------------------------------------


#------------------------------------------------------------------------------------------------------------------------------------
# This class acts a base class for all tests genearting only ifile.
# This class also adds a sanity test to the SphngBase class.
# This class will be used for all Single Node, strong and weak scaling tests.
#------------------------------------------------------------------------------------------------------------------------------------
class SphngBase_ifile(SphngBase):
    def __init__(self):
        super().__init__()
        self.prerun_cmds = ['rm -rf fort* TEST* notify ifile sphng_setup.o']
        self.executable_opts = ['initial ifile < ./setup.txt &> sphng_setup.o']

    @sanity_function
    def validate_ifile_generation(self):
        return sn.assert_true(os.path.exists('ifile'))

#------------------------------------------------------------------------------------------------------------------------------------
# End of base class for ifile.
#------------------------------------------------------------------------------------------------------------------------------------



#------------------------------------------------------------------------------------------------------------------------------------
# This class acts as a base class for the evolutions stage.
# This clsss adds a sanity test for the evolution stage.
# This class will be used in the evolition stage for all Single Node, strong and weak scaling tests. 
#------------------------------------------------------------------------------------------------------------------------------------
class SphngBase_evolution(SphngBase):
    def __init__(self):
        super().__init__()
        self.executable_opts = ['evolution ifile']

        reference = {
         'dial:slurm-local': {
             'Total elapsed time:':  (10, None, None, 'minutes'),
                             }
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
#------------------------------------------------------------------------------------------------------------------------------------
# End of base class for evolition stage.
#------------------------------------------------------------------------------------------------------------------------------------ 


#------------------------------------------------------------------------------------------------------------------------------------
# Single Node test class definition starts here.
# This class is for generating the ifile which is the first step in running Sphng.
# Ifile:- Acts as a input to the evolution stage of Sphng.
# We do not need to decorate this class as it will be used as a fixture and this will cause it to run as a separate test.
#------------------------------------------------------------------------------------------------------------------------------------
class Sphng_Single_Node_ifile(SphngBase_ifile):
    
    mpi_tasks = parameter(2**i for i in range(0,8))

    def __init__(self):
        super().__init__()
        self.num_tasks = self.mpi_tasks           # Total number of mpi tasks.
        self.num_tasks_per_node = self.mpi_tasks  # MPi tasks on one node. Here it will be same as total mpi tasks.
        
    @run_after('setup')
    def set_env_variables(self):

        if self.current_partition.processor.num_cpus_per_core > 1:
            self.core_count_1_node = int(self.current_partition.processor.num_cpus/self.current_partition.processor.num_cpus_per_core)
        else:    
            self.core_count_1_node = self.current_partition.processor.num_cpus

        self.thread_count = str(int(self.core_count_1_node/self.num_tasks_per_node))
        
        self.descr = ('Running Sphng (Ifile) on ' + str(self.num_tasks_per_node) +' tasks and ' + \
                       self.thread_count +  ' threads per node')

        self.variables= {
            'OMP_NUM_THREADS':self.thread_count,
            'OMP_PLACES':'cores'
        }


# This class runs the evolution stage of the Sphng.
@rfm.simple_test
class Sphng_Single_Node_evolution(SphngBase_evolution):
    
    tags = {"Single_node"}

    # Define the fixture here. It also acts a test on which the current test depends.
    # By defining the fixture, we can access the properties associates with the respective test such as num_tasks.
    Ifile_fixture = fixture(Sphng_Single_Node_ifile, scope = 'session')

    def __init__(self):
        super().__init__()
    
    @run_after('setup')
    def set_sourcedir_and_job_params(self):     
        self.num_tasks = self.Ifile_fixture.mpi_tasks
        self.num_tasks_per_node = self.Ifile_fixture.mpi_tasks
        self.thread_count = self.Ifile_fixture.thread_count

        self.descr = ('Running Sphng (Evolution) on ' + str(self.num_tasks_per_node) +' tasks and ' + \
                       self.thread_count +  ' threads per node')

        self.variables= {
            'OMP_NUM_THREADS':self.thread_count,
            'OMP_PLACES':'cores'
        }

        self.sourcesdir = os.path.join(self.Ifile_fixture.stagedir,'')

#------------------------------------------------------------------------------------------------------------------------------------
# End of Single node cases.
#------------------------------------------------------------------------------------------------------------------------------------





#------------------------------------------------------------------------------------------------------------------------------------
# Strong Scaling class Definitions Starts here.
# This class is for generating the ifile which is the first step in running Sphng.
#------------------------------------------------------------------------------------------------------------------------------------
class Sphng_Strong_Scaling_ifile(SphngBase_ifile):

    num_nodes = parameter(2**i for i in range(0,5))

    def __init__(self):
        super().__init__()
        self.num_tasks = 16                                             #Hard coded because this gave the  best performance.
        self.num_tasks_per_node = int(self.num_tasks/self.num_nodes)
        
    @run_after('setup')
    def set_env_variables(self):
            
        if self.current_partition.processor.num_cpus_per_core > 1:
            self.core_count_1_node = int(self.current_partition.processor.num_cpus/self.current_partition.processor.num_cpus_per_core)
        else:    
            self.core_count_1_node = self.current_partition.processor.num_cpus

        self.thread_count = str(int(self.core_count_1_node/self.num_tasks_per_node))

        self.descr = ('Running Sphng (Ifile) on ' + str(self.num_nodes) + ' nodes with ' + \
                       str(self.num_tasks_per_node) + ' tasks per node and ' + self.thread_count + ' threads per node')

        self.variables= {    
                        'OMP_NUM_THREADS':self.thread_count,
                        'OMP_PLACES':'cores'
                        }


# This class runs the evolution stage of the Sphng.
@rfm.simple_test
class Sphng_Strong_Scaling_evolution(SphngBase_evolution):

    tags = {"Strong_scaling"}
    
    # Define the fixture here. It also acts a test on which the current test depends.
    # By defining the fixture, we can access the properties associates with the respective test such as num_tasks.
    Ifile_fixture = fixture(Sphng_Strong_Scaling_ifile, scope = 'session')

    def __init__(self):
        super().__init__()
    
    @run_after('setup')
    def set_sourcedir_and_job_params(self):     
        self.num_tasks = self.Ifile_fixture.num_tasks
        self.num_tasks_per_node = self.Ifile_fixture.num_tasks_per_node
        self.thread_count = self.Ifile_fixture.thread_count
        
        self.descr = ('Running Sphng (Evolution) on ' + str(self.Ifile_fixture.num_nodes) + ' nodes with ' +\
                       str(self.num_tasks_per_node) + ' tasks per node and ' + self.thread_count +  ' threads per node')

        self.variables= {
            'OMP_NUM_THREADS':self.thread_count,
            'OMP_PLACES':'cores'
        }

        self.sourcesdir = os.path.join(self.Ifile_fixture.stagedir,'')
#------------------------------------------------------------------------------------------------------------------------------------
# End of strong scaling cases.
#------------------------------------------------------------------------------------------------------------------------------------



#------------------------------------------------------------------------------------------------------------------------------------
# Weak Scaling class Definitions Starts here.
# This class is for generating the ifile which is the first step in running Sphng.
#------------------------------------------------------------------------------------------------------------------------------------
class Sphng_Weak_Scaling_ifile(SphngBase_ifile):

    num_nodes = parameter(2**i for i in range(0,5))

    def __init__(self):
        super().__init__()
        self.num_tasks = 16 #Hard coded because this gave the  best performance.
        self.num_tasks_per_node = int(self.num_tasks/self.num_nodes)

    @run_after('setup')
    def set_env_variables(self):

        if self.current_partition.processor.num_cpus_per_core > 1:
            self.core_count_1_node = int(self.current_partition.processor.num_cpus/self.current_partition.processor.num_cpus_per_core)
        else:    
            self.core_count_1_node = self.current_partition.processor.num_cpus

        self.thread_count = str(int(self.core_count_1_node/self.num_tasks_per_node))

        self.descr = ('Running Sphng (Ifile) on ' + str(self.num_nodes) + ' nodes with ' + \
                       str(self.num_tasks_per_node) + ' tasks per node and ' + self.thread_count +  ' threads per node')

        self.variables= {
                        'OMP_NUM_THREADS':self.thread_count,
                        'OMP_PLACES':'cores'
                        }

        self.prerun_cmds = ['cp weak_n' + str(self.num_nodes) +'/inspho .', 'cp weak_n'+ str(self.num_nodes) + '/setup.txt .']


# This class runs the evolution stage of the Sphng.
@rfm.simple_test
class Sphng_Weak_Scaling_evolution(SphngBase_evolution):
    
    tags = {"Weak_scaling"}

    # Define the fixture here. It also acts a test on which the current test depends.
    # By defining the fixture, we can access the properties associates with the respective test such as num_tasks.
    Ifile_fixture = fixture(Sphng_Weak_Scaling_ifile, scope = 'session')

    def __init__(self):
        super().__init__()
    
    @run_after('setup')
    def set_sourcedir_and_job_params(self):     
        self.num_tasks = self.Ifile_fixture.num_tasks
        self.num_tasks_per_node = self.Ifile_fixture.num_tasks_per_node
        self.thread_count = self.Ifile_fixture.thread_count
        self.descr = ('Running Sphng (Evolution) on ' + str(self.Ifile_fixture.num_nodes) + ' nodes with ' +\
                       str(self.num_tasks_per_node) + ' tasks per node and ' + self.thread_count +  ' threads per node')

        self.variables= {
            'OMP_NUM_THREADS':self.thread_count,
            'OMP_PLACES':'cores'
        }

        self.sourcesdir = os.path.join(self.Ifile_fixture.stagedir,'')
#------------------------------------------------------------------------------------------------------------------------------------
# End of weak scaling.
#------------------------------------------------------------------------------------------------------------------------------------


