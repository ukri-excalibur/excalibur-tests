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
    url = "https://github.com/NCAS-CMS/hpcg_27ptStencil/archive/refs/tags/1.0.tar.gz"

    version(
        "1.0", sha256= "60dbd50e81cb284e9ab3f1b5564f2a9cb89bf438f5a56f33c4300afbc1df8780"
    )

    version(
        "hpcg_lfric", url="https://github.com/NCAS-CMS/hpcg_27ptStencil/archive/refs/tags/temp240223.tar.gz",
        sha256="493b37a673ddc59a0d0f9c6dd80e8ad371433f1ca70567be8c7c5cc5a9330bcf"
    )        
    depends_on("mpi")

    maintainers = ["someone", "myself"]
#    def edit(self, spec, prefix):

#        makefile FileFilter("Makefile")
#        makefile.filter('arch = UNKNOWN', 'arch = Linux_MPI')
#        # Make the `sombrero.sh` driver relocatable
#        dhc_hpcg_sh = FileFilter(join_path(self.stage.source_path, "dhc_hpcg.sh"))
#        dhc_hpcg_dir = join_path(prefix.bin, "dhc_hpcg")
#        dhc_hpcg_sh.filter("dhc_hpcg/", "{0}/".format(dhc_hpcg_dir))

    @property
    def build_targets(self):
        ''' Makefile has no install, but spack seems to want one for this package, so do build instead of install here (or inherit something else??) '''
        return ['arch=Linux_MPI', "CXXFLAGS='-DHPCG_NO_OPENMP'"]#, 'install']
#        return ['clean']

#    @property
#    def install_targets(self):
#    def build_targets(self):
#        return ['arch=Linux_MPI', "CXXFLAGS='-O3 -ffast-math -ftree-vectorize'"]#, 'install']
#        ''' Makefile has no install, but spack seems to want one for this package, so do build instead of install here (or inherit something else??) '''
#        return ['arch=Linux_MPI', "CXXFLAGS='-DHPCG_NO_OPENMP'"]#, 'install']
    
    def install(self, spec, prefix):
        ''' Makefile has no install '''
        mkdirp(prefix.bin)
        import os;print("CHECK THAT ", os.getcwd(), "/bin/xhpcg exists")
        install('bin/xhpcg', prefix.bin)

#class Hpcg_LFRic(HpcgExcalibur):
#    # Should be the same as above, but with a change to the URL to extract the code
#
#    url = "https://github.com/NCAS-CMS/hpcg_27ptStencil/tarball/lfric_stencil_data"
#    # sha256= 61c0a5cd8c95eeb7acc14be4fe006b823386e29b0684de114db14e5b10043570

