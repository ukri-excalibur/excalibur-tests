# Copyright 2023 University College London (UCL) Research Software Development
# Group.  See the top-level LICENSE file for details.
#
# SPDX-License-Identifier: Apache-2.0

import glob
import gzip
import io
import os
import urllib.request
import tarfile
import reframe as rfm
from reframe.core.backends import getlauncher
import reframe.utility.sanity as sn
from benchmarks.modules.utils import SpackTest

# Download input files.  They are compressed tarballs, but we want to extract
# only certain files.  `url` is the source URL, `match` is a string matching
# the path of the files or directories we want to extract, `dest` is the
# directory where to extract the files.
def download(url, match, dest):
    try:
        tarball_gz = urllib.request.urlopen(url).read()
        tarball = gzip.decompress(tarball_gz)
        tfile = tarfile.TarFile(fileobj=io.BytesIO(tarball))
        members = [tarinfo for tarinfo in tfile.getmembers()
                   if tarinfo.name.startswith(match)]
        tfile.extractall(dest, members=members)
    except urllib.request.HTTPError:
        print(f'ERROR retrieving {url}')
        raise


@rfm.simple_test
class OpenMMBenchmark(SpackTest):
    valid_systems = ['+gpu']
    valid_prog_environs = ['default']
    spack_spec = 'openmm@7.7.0 +cuda'

    time_limit = '1h'

    executable = 'python3'

    # Directory where the input files will be downloaded, and copied from into
    # the stage directory.
    sourcesdir = os.path.join(os.path.dirname(__file__), 'input')

    num_tasks = 1
    num_tasks_per_node = 1
    num_cpus_per_task = required
    num_gpus_per_node = 1

    @run_before('compile')
    def setup_build_system(self):
        self.build_system.specs = [self.spack_spec]

    @run_after('setup')
    def setup_variables(self):
        self.executable_opts = [os.path.join(self.prefix, 'openmm-gpu-bench.py')]
        self.set_var_default(
            'num_cpus_per_task',
            self.current_partition.processor.num_cpus)
        self.env_vars['OMP_NUM_THREADS'] = f'{self.num_cpus_per_task}'
        self.env_vars['OMP_PLACES'] = 'cores'
        self.extra_resources = {
            'mpi': {'num_slots': self.num_tasks * self.num_cpus_per_task},
            'gpu': {'num_gpus_per_node': self.num_gpus_per_node},
        }

    # Download input files into the sources directory
    @run_after('setup')
    def download_input(self):
        # Create sources dir, if it doesn't exist already.
        os.makedirs(self.sourcesdir, exist_ok=True)

        # Fetch the toppar tarball, and extract the file we need.
        charmm_basename = 'top_all27_prot_lipid.rtf'
        charmm_file = os.path.join(self.sourcesdir, charmm_basename)
        if not os.path.exists(charmm_file):
            download('http://mackerell.umaryland.edu/download.php?filename=CHARMM_ff_params_files/toppar_c35b2_c36a2.tgz',
                     f'toppar/{charmm_basename}',
                     self.sourcesdir)
            os.rename(os.path.join(self.sourcesdir, 'toppar', charmm_basename),
                      charmm_file)
            os.rmdir(os.path.join(self.sourcesdir, 'toppar'))

        # Fetch the NAMD tarball, and extract the files we need.
        namd_file = os.path.join(self.sourcesdir, 'benchmark.psf')
        if not os.path.exists(namd_file):
            download('https://www.hecbiosim.ac.uk/benchmark-files/namd.tar.gz',
                     'namd/1400k-atoms',
                     self.sourcesdir)
            for f in glob.glob(f'{self.sourcesdir}/namd/1400k-atoms/*'):
                os.rename(f, os.path.join(self.sourcesdir, os.path.basename(f)))
            os.rmdir(os.path.join(self.sourcesdir, 'namd', '1400k-atoms'))
            os.rmdir(os.path.join(self.sourcesdir, 'namd'))

    @run_before('run')
    def replace_launcher(self):
        # For this benchmark we don't use MPI at all, so we always force the
        # local launcher:
        # <https://reframe-hpc.readthedocs.io/en/v4.1.3/tutorial_advanced.html#replacing-the-parallel-launcher>.
        self.job.launcher = getlauncher('local')()

    @run_before('sanity')
    def set_sanity_patterns(self):
        self.sanity_patterns = sn.assert_found('Done!', self.stdout)
