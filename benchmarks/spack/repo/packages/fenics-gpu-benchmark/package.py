# Copyright 2013-2025 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack.package import *

class FenicsGpuBenchmark(CMakePackage, CudaPackage, ROCmPackage):
    "A weak-scaling performance test for the FEniCS Finite Element Package with GPU support"

    homepage = "https://github.com/FEniCS/performance-test"
    git = "https://github.com/FEniCS/performance-test.git"

    version("main", tag="chris/gpu")

    variant("float32", default=False)
    depends_on("fenics-dolfinx@main")
    depends_on("py-fenics-ffcx@main", type="build")
    depends_on("py-setuptools", type="build")
    depends_on("py-fenics-ufl@main", type="build")
    depends_on("mpi")
    depends_on("hip", when="+rocm")
    depends_on("cuda", when="+cuda")

    with when("+rocm"):
        depends_on("rocm-core")
        depends_on("rocsparse")
        depends_on("rocrand")
        depends_on("rocthrust")
        depends_on("rocprim")

    with when("+cuda"):
        depends_on("thrust")

    root_cmakelists_dir = "gpu"

    def cmake_args(self):
        opts = []
        if "+rocm" in self.spec:
            opts += [self.define("amd", True)]
        if "+cuda" in self.spec:
            opts += [self.define("nvidia", True)]
        if "+float32" in self.spec:
            opts += [self.define("SCALAR_TYPE", "float32")]
        return opts
