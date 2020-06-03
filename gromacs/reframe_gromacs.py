''' Playground for seeing what reframe can do.

    Run using something like:
        
        conda activate hpc-tests
        reframe/bin/reframe -C reframe-settings.py -c gromacs-2016.4/ --run # --performance-report

 TODO:
'''

import reframe as rfm
import reframe.utility.sanity as sn
import os, sys, urllib
sys.path.append('.')
import reframe_extras

from reframe.core.logging import getlogger

@rfm.simple_test
class Gromacs_SmallBM(rfm.RunOnlyRegressionTest):
    def __init__(self):
        """ Run Archer 'small' (single-node) Gromacs benchmark.

            Based on https://github.com/hpc-uk/archer-benchmarks/blob/master/apps/GROMACS/1400k-atoms/run/CSD3-Skylake/submit.slurm

            TODO:
            - add perf and sanity patterns
            - parameterise for different numbers of cores
        """

        self.valid_systems = ['*']
        self.valid_prog_environs = ['spack-gnu7-openmpi4']

        num_nodes = 1
        cpu_factor = 0.5 # because SMT is on on alaska
        max_cpus = int(reframe_extras.slurm_node_info()[0]['CPUS']) # 0: arbitrarily use first nodes info
        num_tasks = int(max_cpus * cpu_factor)
        casename = 'benchmark'
        resfile=casename
        
        self.sourcesdir = os.path.join(self.prefix, 'downloads') # i.e. downloads/ will be alongside this file
        self.executable = 'gmx_mpi'
        self.executable_opts = ['mdrun', '-s', '%s.tpr' % casename, '-g', resfile, '-noconfout']
        self.num_tasks = num_tasks
        self.num_tasks_per_node = int(num_tasks / num_nodes)
        self.exclusive_access = True

        self.keep_files = ['bencmark.log']
        self.sanity_patterns = sn.assert_found(r'.*', self.stdout) # TODO: FIXME:
        self.perf_patterns = None # TODO: FIXME:

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
        