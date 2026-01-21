# Copyright 2013-2023 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

class FenicsBenchmark(CMakePackage):
    "A weak-scaling performance test for the FEniCS Finite Element Package"

    homepage = "https://github.com/FEniCS/performance-test"
    git = "https://github.com/FEniCS/performance-test.git"

    depends_on("fenics-dolfinx@0.9.0")
    depends_on("py-fenics-ffcx@0.9.0", type="build")
    depends_on("py-setuptools", type="build")
    depends_on("py-fenics-ufl@2024.2.0", type="build")

    version("0.9.0", tag="v0.9.0")


    root_cmakelists_dir = "src"
