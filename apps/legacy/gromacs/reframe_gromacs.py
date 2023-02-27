""" Performance test using Gromacs molecular dynamics code: http://www.gromacs.org/

    See README.md for details.
"""

import reframe as rfm
import reframe.utility.sanity as sn
import os, sys, urllib, shutil, itertools
sys.path.append('.')
from modules.reframe_extras import scaling_config
from modules.utils import parse_time_cmd
from reframe.core.logging import getlogger

# define parameterisation for all possible partitions as combination of benchmark cases and run sizes:
CASES = ['1400k-atoms', '61k-atoms', '3000k-atoms']
sizes = scaling_config()
params = [[case] + list(size) for case, size in itertools.product(CASES, sizes)] # flatten to a single list per element

@rfm.parameterized_test(*params)
class Gromacs_HECBioSim(rfm.RunOnlyRegressionTest):
    """ Run HECBioSim Gromacs benchmarks.

        Runs for environments named "gromacs" only.

        This is parameterised to run on 1 node up to as many nodes are available.
        Each run uses the same number of processes per node as there are physical cores.

        Also handles download/unpacking benchmark files.

        Args:
            casename: str, directory name from the HECBioSim benchmark download, one of:
                1400k-atoms  20k-atoms  3000k-atoms  465k-atoms  61k-atoms
            test_size: Number of nodes to use, possibly as fraction of partition size. See `modules.reframe_extras.ScalingTest.partition_fraction`.
    """
    def __init__(self, casename, part, num_tasks, num_tasks_per_node):
        
        #self.name = 'Gromacs_%s_%s' % (casename.split('-')[0], test_size) # e.g. Gromacs_1400k_-2

        self.casename = casename
        self.num_tasks = num_tasks
        self.num_tasks_per_node = num_tasks_per_node
        self.num_nodes = int(num_tasks / num_tasks_per_node)
        
        self.tags |= {casename, 'num_procs=%i' % self.num_tasks, 'num_nodes=%i' % self.num_nodes}

        self.logfile = casename + '.log'
        
        self.valid_systems = [part]
        self.valid_prog_environs = ['gromacs']
        
        # created by download_benchmarks():
        self.sourcesdir = os.path.join(self.prefix, 'downloads', 'gromacs', self.casename)

        self.prerun_cmds = ['time \\']
        self.executable = 'gmx_mpi'
        self.executable_opts = ['mdrun', '-s', 'benchmark.tpr', '-g', self.logfile, '-noconfout'] #, '-ntomp', '1'] add this to turn off threading
        self.exclusive_access = True
        self.time_limit = '1h'
        
        self.keep_files = [self.logfile]
        self.sanity_patterns = sn.assert_found(r'Performance:', self.stderr)
        self.perf_patterns = {
            # from gromacs output:
            'ns_per_day': sn.extractsingle(r'Performance:\s+(\S+)\s+(\S+)', self.logfile, 1, float),
            'hour_per_ns':  sn.extractsingle(r'Performance:\s+(\S+)\s+(\S+)', self.logfile, 2, float),
            'core_t': sn.extractsingle(r'\s+Time:\s+([\d.]+)\s+([\d.]+)\s+[\d.]+', self.logfile, 1, float), # "Core t (s)"
            'wall_t': sn.extractsingle(r'\s+Time:\s+([\d.]+)\s+([\d.]+)\s+[\d.]+', self.logfile, 2, float), # "Wall t (s)"
            # from `time`:
            'runtime_real': sn.extractsingle(r'^real\s+(\d+m[\d.]+s)$', self.stderr, 1, parse_time_cmd),
        }
        self.reference = {
            '*': {
                'ns_per_day': (0, None, None, 'ns/day'),
                'hour_per_ns': (0, None, None, 'hour/ns'),
                'core_t': (0, None, None, 's'),
                'wall_t': (0, None, None, 's'),
                'runtime_real': (0, None, None, 's'),
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
    