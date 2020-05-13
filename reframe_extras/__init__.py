""" Extra functionality for reframe

    TODO: refactor into modules
"""

import sys
print(sys.path)

import reframe as rfm
from reframe.core.buildsystems import BuildSystem
from reframe.core.logging import getlogger

import os, shutil, subprocess
from pprint import pprint

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