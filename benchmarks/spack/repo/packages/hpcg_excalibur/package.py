# Copyright 2013-2022 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from os import symlink

from spack.package import *


#class Dhc_hpcg(MakefilePackage):
class HpcgExcalibur(MakefilePackage):
    "A next-generation conjugate gradient benchmark from computational particle physics"

    homepage = "https://github.com/NCAS-CMS/hpcg_27ptStencil"
    url = "https://github.com/NCAS-CMS/hpcg_27ptStencil/archive/refs/tags/stencil_180523.tar.gz"

    version(
        "stencil_180523", sha256= "b82517ade50c7ef2d92176b411328ac705a42c3b1d954a5ec3e998a1694481dc"
    )

    version(
        "hpcg_lfric",
        url="https://github.com/NCAS-CMS/hpcg_27ptStencil/archive/refs/tags/lfric_180523.tar.gz",
        sha256="fb3dec7c7c0727922fac91ec487dd42b8a62f56d9bbda61b97e351aee52e45ed"
    )        

    version(
        "hpcg_original", url="https://github.com/NCAS-CMS/hpcg_27ptStencil/archive/refs/tags/original_branchpoint.tar.gz",
        sha256="1a1928189828f43b8391258d051887762865ed63e54aaabbe4059c14fa788529"
    )
    
    depends_on("openmpi")

    maintainers = ["Dave_Case"]

    @property
    def build_targets(self):
        ''' Makefile has no install, but spack seems to want one for this package, so do build instead of install here (or inherit something else??) '''
#        return ['arch=Linux_MPI']
        return ['arch=Linux_MPI',  "CXXFLAGS=$(HPCG_DEFS) -O3"]

#    @property
#    def install_targets(self):
#    def build_targets(self):
#        return ['arch=Linux_MPI', "CXXFLAGS='-O3 -ffast-math -ftree-vectorize'"]#, 'install']
#        ''' Makefile has no install, but spack seems to want one for this package, so do build instead of install here (or inherit something else??) '''
#        return ['arch=Linux_MPI', "CXXFLAGS='-DHPCG_NO_OPENMP'"]#, 'install']
    
    def install(self, spec, prefix):
        ''' Makefile has no install '''
        mkdirp(prefix.bin)
        # copy dinodump.dat to the bin dir (same place as bin as easy to find with reframe)
        if self.spec.satisfies("@hpcg_lfric"):
            import shutil
            shutil.copyfile('dinodump.dat', prefix.bin + '/dinodump.dat')
        install('bin/xhpcg', prefix.bin)
