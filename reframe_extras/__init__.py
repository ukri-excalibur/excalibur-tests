""" Extra functionality for reframe

    TODO: refactor into modules
"""

import reframe as rfm
from reframe.core.buildsystems import BuildSystem
from reframe.core.logging import getlogger

import os, shutil

class CachedCompileOnlyTest(rfm.CompileOnlyRegressionTest):
    """ NB: This manipulates `sourcesdir` in a run_before('compile') step - so don't do that in any test using this.
        sets self.build_path to an absolute path if a preexisting build was used.
        assumes self.executable is correct (i.e. consistent between original compile and a non-compiling run)
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