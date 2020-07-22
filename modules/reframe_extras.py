""" Extra functionality for reframe

"""

import reframe as rfm
from reframe.core.buildsystems import BuildSystem
from reframe.core.logging import getlogger
from reframe.core.launchers import JobLauncher
import reframe.utility.sanity as sn

import os, shutil, subprocess, shlex
from pprint import pprint

class CachedRunTest(rfm.RegressionTest):
    """ Mixin. TODO: document properly.

        Classes using this can be derive from `rfm.RunOnlyRegressionTest`
        Assumes saved output files are in a directory `cache/` in same parent directory (and with same directory tree) as the `output/` and `stage/` directories.

        set self.use_cache to True or a path relative to cwd.
    
        NB Any class using this MUST NOT change self.executable in a method decorated with `@rfm.run_before('run')` as that will override functionality here.
    """

    @rfm.run_before('run')
    def no_run(self):
        """ Turn the run phase into a no-op. """

        if self.use_cache:
            with open(os.path.join(self.stagedir, 'noop.sh'), 'w') as noop:
                noop.write('#!/bin/bash\necho "noop $@"\n')
            self.executable = "./noop.sh"

    @rfm.run_after('run')
    def copy_saved_output(self):
        """ Copy saved output files to stage dir. """

        if self.use_cache:
            # find the part of the path common to both output and staging:
            rtc = rfm.core.runtime.runtime()
            tree_path = os.path.relpath(self.outputdir, rtc.output_prefix)
            
            cache_root = 'cache' if self.use_cache == True else self.use_cache

            saved_output_dir = os.path.join(cache_root, tree_path)
            
            if not os.path.exists(saved_output_dir) or not os.path.isdir(saved_output_dir):
                raise ValueError("cached output directory %s does not exist or isn't a directory" % os.path.abspath(saved_output_dir))

            import distutils.dir_util
            distutils.dir_util.copy_tree(saved_output_dir, self.stagedir)


class CachedCompileOnlyTest(rfm.CompileOnlyRegressionTest):
    """ A compile-only test with caching of binaries between `reframe` runs.
    
        Test classes derived from this class will save `self.executable` to a ./builds/{system}/{partition}/{environment}/{self.name}` directory after compilation.
        However if this path (including the filename) exists before compilation (i.e. on the next run):
            - No compilation occurs
            - `self.sourcesdir` is set to this directory, so `reframe` will copy the binary to the staging dir (as if compilation had occured)
            - A new attribute `self.build_path` is set to this path (otherwise None)

        Note that `self.sourcesdir` is only manipulated if no compilation occurs, so compilation test-cases which modify this to specify the source directory should be fine.

        TODO: Make logging tidier - currently produces info-level (stdout by default) messaging on whether cache is used.
    """
    @rfm.run_before('compile')
    def conditional_compile(self):
        build_dir = os.path.abspath(os.path.join('builds', self.current_system.name, self.current_partition.name, self.current_environ.name, self.name))
        build_path = os.path.join(build_dir, self.executable)
        if os.path.exists(build_path):
            self.build_path = build_path
            getlogger().info('found exe at %r', self.build_path)
            self.build_system = NoBuild()
            self.sourcesdir = build_dir # means reframe will copy the exe back in
        else:
            self.build_path = None

    @rfm.run_after('compile')
    def copy_executable(self):
        if not self.build_path: # i.e. only if actually did a compile:
            self.exes_dir = os.path.join('builds', self.current_system.name, self.current_partition.name, self.current_environ.name, self.name)
            exe_path = os.path.join(self.stagedir, self.executable)
            build_path = os.path.join(self.exes_dir, self.executable)
            build_dir = os.path.dirpath(build_path) # self.executable might include a directory
            if not os.path.exists(build_dir):
                os.makedirs(build_dir)
            shutil.copy(exe_path, build_path)
            getlogger().info('copied exe to %r', build_path)

class NoBuild(BuildSystem):
    """ A no-op build system """
    def __init__(self):
        super().__init__()
    def emit_build_commands(self, environ):
        return []

def slurm_node_info():
    """ Get information about slurm nodes.
    
        Returns a sequence of dicts, one per node with keys/values all strs as follows:
            "NODELIST": name of node
            "NODES": number of nodes
            "PARTITION": name of partition, * appended if default
            "STATE": e.g. "idle"
            "CPUS": str number of cpus
            "S:C:T": Extended processor information: number of sockets, cores, threads in format "S:C:T"
            "MEMORY": Size of memory in megabytes
            "TMP_DISK": Size of temporary disk space in megabytes
            "WEIGHT": Scheduling weight of the node
            "AVAIL_FE": ?
            "REASON": The reason a node is unavailable (down, drained, or draining states) or "none"
        See `man sinfo` for `sinfo --Node --long` for full details.

        TODO: add partition selection? with None being current one (note system partition != slurm partition)
    """
    nodeinfo = subprocess.run(['sinfo', '--Node', '--long'], capture_output=True).stdout.decode('utf-8') # encoding?

    nodes = []
    lines = nodeinfo.split('\n')
    header = lines[1].split() # line[0] is date/time
    for line in lines[2:]:
        line = line.split()
        if not line:
            continue
        nodes.append({})
        for ci, key in enumerate(header):
            nodes[-1][key] = line[ci]
    return nodes


class Scheduler_Info(object):
    def __init__(self):
        """ Information from the scheduler.

            Attributes:
                num_nodes: number of nodes
                pcores_per_node: number of physical cores per node
                lcores_per_node: number of logical cores per node
        """
        # TODO: handle scheduler not being slurm!
        nodeinfo = slurm_node_info()

        self.num_nodes = len(nodeinfo)
        cpus = [n['S:C:T'] for n in nodeinfo]
        if not len(set(cpus)) == 1:
            raise ValueError('CPU description differs between nodes, cannot define unique value')
        sockets, cores, threads = [int(v) for v in cpus[0].split(':')] # nb each is 'per' the preceeding
        self.sockets_per_node = sockets
        self.pcores_per_node = sockets * cores
        self.lcores_per_node = sockets * cores * threads

    def __str__(self):

        descr = ['%s=%s' % (k, getattr(self, k)) for k in ['num_nodes', 'sockets_per_node', 'pcores_per_node', 'lcores_per_node']]

        return 'Scheduler_Info(%s)' % (', '.join(descr))

def sequence(start, end, factor):
    """ Like `range()` but each term is `factor` * previous term.

        `start` is inclusive, `end` is exclusive.

        Returns a list.
    """

    values = []
    v = start
    while v < end:
        values.append(v)
        v *= factor
    return values

if __name__ == '__main__':
    # will need something like:
    # [hpc-tests]$ PYTHONPATH='reframe' python modules/reframe_extras.py
    print(Scheduler_Info())
    