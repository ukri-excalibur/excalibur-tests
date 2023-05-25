# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from os import symlink

from spack.package import *

class HpcgExcalibur(MakefilePackage):
    "A next-generation conjugate gradient benchmark from computational particle physics"

    homepage = "https://github.com/NCAS-CMS/hpcg_27ptStencil"
    url = "https://github.com/NCAS-CMS/hpcg_27ptStencil/archive/refs/tags/stencil_180523.tar.gz"

    version(
        "stencil_180523",
        url = "https://github.com/NCAS-CMS/hpcg_27ptStencil/archive/refs/tags/stencil_180523.tar.gz",
        sha256= "b82517ade50c7ef2d92176b411328ac705a42c3b1d954a5ec3e998a1694481dc"
    )

    version(
        "hpcg_lfric",
        url="https://github.com/NCAS-CMS/hpcg_27ptStencil/archive/refs/tags/lfric_250523.tar.gz",
        sha256="fa2824890175489e5ad43e4d30d2fd41334777b4ef9c95d798536fc9b8766229"
    )        

    version(
        "hpcg_original",
        url="https://github.com/NCAS-CMS/hpcg_27ptStencil/archive/refs/tags/original_branchpoint.tar.gz",
        sha256="1a1928189828f43b8391258d051887762865ed63e54aaabbe4059c14fa788529"
    )
    
    depends_on("openmpi")

    maintainers = ["dcaseGH"]

    @property
    def build_targets(self):
        ''' Can change flags and modify make file for other MPI implementations '''
        return ['arch=Linux_MPI',  "CXXFLAGS=$(HPCG_DEFS) -O3"]

    def install(self, spec, prefix):
        ''' Makefile has no install - can just copy things which are required '''
        mkdirp(prefix.bin)
        # copy dinodump.dat and hpcg.dat to the spack bin
        if self.spec.satisfies("@hpcg_lfric"):
            import shutil
            shutil.copyfile('dinodump.dat', prefix.bin + '/dinodump.dat')
            shutil.copyfile('bin/hpcg.dat', prefix.bin + '/hpcg.dat')
        install('bin/xhpcg', prefix.bin)
