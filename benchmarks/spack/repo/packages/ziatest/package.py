# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)
import spack.build_systems.makefile
from spack.package import *


class Ziatest(MakefilePackage):
    """Realistic assessment of both launch and wireup requirements of MPI applications"""

    homepage = "https://gitlab.com/NERSC/N10-benchmarks/ziatest"
    git = "https://gitlab.com/NERSC/N10-benchmarks/ziatest"
    maintainers("giordano")

    version("main", branch="main")

    depends_on("c", type="build")
    depends_on("mpi")

    patch("Add-missing-sys-time.h-header-file.patch")
    patch("Improve-check-for-number-of-arguments.patch")

    @property
    def build_targets(self):
        spec = self.spec
        return [
            f"MPICC={spec['mpi'].mpicc}",
        ]

    def install(self, spec, prefix):
        mkdir(prefix.bin)
        install("ziatest", prefix.bin)
        install("ziaprobe", prefix.bin)
