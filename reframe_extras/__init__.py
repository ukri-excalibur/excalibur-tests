""" Extra functionality for reframe

    TODO: refactor into modules
"""

import reframe as rfm
from reframe.core.buildsystems import BuildSystem
from reframe.core.logging import getlogger
from reframe.core.launchers import JobLauncher

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
    
        Returns a sequence of dicts, one per node.
        TODO: document keys - are as per `sinfo --Node --long`

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


# you don't need this, you can just use e.g.:
# @rfm.run_before('run')
#     def add_launcher_options(self):
#         self.job.launcher.options = ['--map-by=xxx']

# class LauncherWithOptions(JobLauncher):
#     """ Wrap a job launcher to provide options.

#         Use like:

#         @rfm.run_after('setup')
#         def modify_launcher(self):
#             self.job.launcher = LauncherWithOptions(self.job.launcher, options=['--bind-to', 'core'])
        
#         TODO: change behaviour depending on launcher type?
#     """
#     def __init__(self, target_launcher, options=None):
#         if options is None:
#             options = []
#         super().__init__()
#         self.self.launcher_options = options
#         self._target_launcher = target_launcher
#         self._wrapper_command = [wrapper_command] + wrapper_options

#     def command(self, job):
#         launcher_cmd = self._target_launcher.command(job) # a list
#         return launcher_cmd[0] + self.launcher_options + launcher_cmd[1:]

def nodeseq(last=1):
    """ Return a sequence of node numbers.
    
        Starts at max nodes reported by slurm and then halves each time down to `last` (inclusive).
    """
    nums = []
    n_nodes = len(slurm_node_info())
    i = 0
    while True:
        n = int(n_nodes/pow(2,i))
        nums.append(n)
        if n <= last:
            return nums
        i += 1

if __name__ == '__main__':
    # will need something like:
    # [hpc-tests]$ PYTHONPATH='reframe' python reframe_extras/__init__.py
    pprint(slurm_node_info())