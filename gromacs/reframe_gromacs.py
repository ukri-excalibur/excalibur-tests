''' Playground for seeing what reframe can do.

    Run using something like:
        
        conda activate hpc-tests
        reframe/bin/reframe -C reframe_config.py -c gromacs/ --run --performance-report

 TODO:
'''

import reframe as rfm
import reframe.utility.sanity as sn
import os, sys, urllib
sys.path.append('.')
import reframe_extras

from reframe.core.logging import getlogger

@rfm.parameterized_test(*[[n] for n in reframe_extras.nodeseq()])
class Gromacs_SmallBM(rfm.RunOnlyRegressionTest, reframe_extras.CachedRunTest):
    def __init__(self, num_nodes):
        """ Run Archer 'small' Gromacs benchmark.

            Based on https://github.com/hpc-uk/archer-benchmarks/blob/master/apps/GROMACS/1400k-atoms/run/CSD3-Skylake/submit.slurm

            This runs on 1 node up to as many nodes are available.
        """

        self.valid_systems = ['*']
        self.valid_prog_environs = ['gromacs']

        cpu_factor = 0.5 # define fraction of cores to use - 0.5 here because alaska has hyperthreading/SMT turned on
        max_cpus = int(reframe_extras.slurm_node_info()[0]['CPUS']) # 0: arbitrarily use first nodes info
        num_tasks = num_nodes * int(max_cpus * cpu_factor)
        casename = 'benchmark'
        resfile=casename
        
        self.sourcesdir = os.path.join(self.prefix, 'downloads') # i.e. downloads/ will be alongside this file
        self.executable = 'gmx_mpi'
        self.executable_opts = ['mdrun', '-s', '%s.tpr' % casename, '-g', resfile, '-noconfout']
        self.num_tasks = num_tasks
        self.num_tasks_per_node = int(num_tasks / num_nodes)
        self.exclusive_access = True
        self.time_limit = None # TODO: set this to something reasonable??

        self.keep_files = ['benchmark.log']
        self.sanity_patterns = sn.assert_found(r'Performance:', self.stderr)
        self.perf_patterns = {
            'ns_per_day': sn.extractsingle(r'Performance:\s+(\S+)\s+(\S+)', 'benchmark.log', 1, float),
            'hour_per_ns':  sn.extractsingle(r'Performance:\s+(\S+)\s+(\S+)', 'benchmark.log', 2, float),
        }
        self.reference = {
            '*': {
                'ns_per_day': (0, None, None, 'ns/day'),
                'hour_per_ns': (0, None, None, 'hour/ns'),
            }
        }

        self.use_cache = False # set to True to debug outputs using cached results
            
        # example output from benchmark.log:
        # <snip>
        #                Core t (s)   Wall t (s)        (%)
        #        Time:    73493.146     1148.330     6400.0
        #                  (ns/day)    (hour/ns)
        # Performance:        1.505       15.947
        # Finished mdrun on rank 0 Wed Jun  3 17:18:58 2020
        #
        # <EOF>
        
        
        # TODO:
        # set norequeue?
        # use openmp?
    
    @rfm.run_before('run')
    def download_benchmark(self):
        """ Download benchmark file from Archer benchmarks gitlab.
        
            NB: This saves it to a persistent location defined by `self.sourcesdir` - reframe will then copy it into the staging dir.
        """

        benchmark_url = 'https://github.com/hpc-uk/archer-benchmarks/blob/master/apps/GROMACS/1400k-atoms/input/benchmark.tpr?raw=true'
        if not os.path.exists(self.sourcesdir):
            os.makedirs(self.sourcesdir, exist_ok=True)
        dest = os.path.join(self.sourcesdir, 'benchmark.tpr')
        if not os.path.exists(dest):
            urllib.request.urlretrieve(benchmark_url, dest)
    
    