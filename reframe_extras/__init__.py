""" Extra functionality for reframe

    TODO: refactor into modules
"""

import reframe as rfm
from reframe.core.buildsystems import BuildSystem
from reframe.core.logging import getlogger

import os, shutil

class CachedCompileOnlyTest(rfm.CompileOnlyRegressionTest):
    """ TODO """
    @rfm.run_before('compile')
    def conditional_compile(self):
        build_dir = os.path.join('builds', self.current_system.name, self.current_partition.name, self.current_environ.name, self.name)
        build_path = os.path.join(build_dir, self.executable)
        if os.path.exists(build_path):
            self.build_path = build_path
            getlogger().info('found exe at %r', self.build_path)
            self.build_system = NoBuild()
            # have to copy it into the stage dir else we get:
            #  Failing phase: compile_wait
            #  OS error: [Errno 2] No such file or directory: '/mnt/nfs/hpc-tests/stage/sausage-newslurm/compute/gnu8-openmpi3/Helloworld_Build/./Helloworld_Build'
            dest = os.path.join(self.stagedir, self.executable)
            shutil.copy(self.build_path, dest)
            getlogger().info('copied to %r', dest)
            self.sourcesdir = None # have to set this to avoid the test dir getting copied over the stage dir         
        else:
            self.build_path = None

    @rfm.run_after('compile')
    def copy_executable(self):
        if not self.build_path: # i.e. actually did a compile:
            self.exes_dir = os.path.join('builds', self.current_system.name, self.current_partition.name, self.current_environ.name, self.name)
            if not os.path.exists(self.exes_dir):
                os.makedirs(self.exes_dir)
            exe_path = os.path.join(self.stagedir, self.executable)
            build_path = os.path.join(self.exes_dir, self.executable)
            shutil.copy(exe_path, build_path)
            getlogger().info('copied exe to %r', build_path)

class NoBuild(BuildSystem):
    def __init__(self):
        super().__init__()
    def emit_build_commands(self, environ):
        return []