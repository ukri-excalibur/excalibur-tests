""" Performance test using Gromacs molecular dynamics code: http://www.gromacs.org/

    Runs benchmarks from HECBioSim: http://www.hecbiosim.ac.uk/benchmarks
    - 61K atom system - 1WDN Glutamine-Binding Protein
    - 1.4M atom system - A Pair of hEGFR Dimers of 1IVO and 1NQL
    - 3M atom system - A Pair of hEGFR tetramers of 1IVO and 1NQL

    Run using e.g.:
        
        cd hpc-tests
        conda activate hpc-tests
        reframe/bin/reframe -C reframe_config.py -c gromacs/ --run --performance-report
"""

import reframe as rfm
import reframe.utility.sanity as sn
import os, sys, urllib, shutil, itertools
sys.path.append('.')
from modules.reframe_extras import sequence, Scheduler_Info, CachedRunTest
from reframe.core.logging import getlogger

# parameterisation:
node_seq = sequence(1, Scheduler_Info().num_nodes + 1, 2)
benchmarks = ['1400k-atoms', '61k-atoms', '3000k-atoms']

@rfm.parameterized_test(*list(itertools.product(benchmarks, node_seq)))
class Gromacs_HECBioSim(rfm.RunOnlyRegressionTest, CachedRunTest):
    """ Run HECBioSim Gromacs benchmarks.

        Runs for environments named "gromacs" only.

        This is parameterised to run on 1 node up to as many nodes are available.
        Each run uses the same number of processes per node as there are physical cores.

        Also handles download/unpacking benchmark files.

        Set `self.use_cache=True` to re-run results processing without actually running
        gromacs again, e.g. during debugging. See `reframe_extras.CachedRunTest` for details.
        
        Args:
            casename: str, directory name from the HECBioSim benchmark download, one of:
                1400k-atoms  20k-atoms  3000k-atoms  465k-atoms  61k-atoms
            num_nodes: int, number of nodes to run on
    """
    def __init__(self, casename, num_nodes):
        

        self.name = 'Gromacs_%s_%i' % (casename.split('-')[0], num_nodes) # e.g. Gromacs_1400k_2
        self.use_cache = False # set to True to debug outputs using cached results

        self.casename = casename
        self.num_nodes = num_nodes

        # these are the ones reframe uses:
        self.num_tasks_per_node = Scheduler_Info().pcores_per_node
        self.num_tasks = self.num_nodes * self.num_tasks_per_node

        self.logfile = casename + '.log'
        
        self.valid_systems = ['*']
        self.valid_prog_environs = ['gromacs']
        
        # created by download_benchmarks():
        self.sourcesdir = os.path.join(self.prefix, 'downloads', 'gromacs', self.casename)

        self.executable = 'gmx_mpi'
        self.executable_opts = ['mdrun', '-s', 'benchmark.tpr', '-g', self.logfile, '-noconfout']
        self.exclusive_access = True
        self.time_limit = None # TODO: set this to something reasonable??
        
        self.keep_files = [self.logfile]
        self.sanity_patterns = sn.assert_found(r'Performance:', self.stderr)
        self.perf_patterns = {
            'ns_per_day': sn.extractsingle(r'Performance:\s+(\S+)\s+(\S+)', self.logfile, 1, float),
            'hour_per_ns':  sn.extractsingle(r'Performance:\s+(\S+)\s+(\S+)', self.logfile, 2, float),
        }
        # TODO: these are basically the same so just keep ns_per_day (higher = better)?
        self.reference = {
            '*': {
                'ns_per_day': (0, None, None, 'ns/day'),
                'hour_per_ns': (0, None, None, 'hour/ns'),
            }
        }

        # example output from logfile:
        # <snip>
        #                Core t (s)   Wall t (s)        (%)
        #        Time:    73493.146     1148.330     6400.0
        #                  (ns/day)    (hour/ns)
        # Performance:        1.505       15.947
        # Finished mdrun on rank 0 Wed Jun  3 17:18:58 2020
        #
        # <EOF>
        
    @rfm.run_before('run')
    def download_benchmarks(self, ):
        """ Download & unpack HECBioSim Gromacs benchmarks
        
            NB: This saves and unpacks it to a persistent location defined by `self.sourcesdir`
                - reframe will then copy it into the staging dir.
        """
        
        benchmark_url = 'http://www.hecbiosim.ac.uk/gromacs-benchmarks/send/2-software/8-gromacs-bench'
        download_dir = os.path.join(self.prefix, 'downloads') # i.e. downloads/ will be alongside this file
        download_dest = os.path.join(download_dir, 'hecbiosim-gromacs.tar.gz')
        download(benchmark_url, download_dest, download_dir)

# TODO: move this into modules
def download(url, download_dest, extract_dir=None):
    """ Download resources with caching.

        Args:
            url: str, url to download from
            download_dest: str, path to download resource at `url` to. This should include the filename
            and also the extension if unpacking is required. If this path exists then `url` will not be downloaded.
            extract_dir: str, path to directory to unpack to, or None if no unpacking is required.
        Directories will be created if required.
        Returns ???
    """

    if not os.path.exists(download_dest):
        download_dir = os.path.dirname(download_dest)
        if not os.path.exists(download_dir):
            os.makedirs(download_dir, exist_ok=True)
        urllib.request.urlretrieve(url, download_dest)
    if extract_dir is not None:
        if not os.path.exists(extract_dir):
            os.makedirs(extract_dir, exist_ok=True)
        shutil.unpack_archive(download_dest, extract_dir)
    