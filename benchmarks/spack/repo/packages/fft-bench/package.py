# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

# ----------------------------------------------------------------------------
# If you submit this package back to Spack as a pull request,
# please first remove this boilerplate and all FIXME comments.
#
# This is a template package file for Spack.  We've put "FIXME"
# next to all the things you'll want to change. Once you've handled
# them, you can save this file and test your package like this:
#
#     spack install fft-bench
#
# You can edit this file again by typing:
#
#     spack edit fft-bench
#
# See the Spack documentation for more information on packaging.
# ----------------------------------------------------------------------------

from spack_repo.builtin.build_systems.generic import Package
from spack.package import *
import os

class FftBench(CMakePackage):
    # URL for FFT Benchmark Github.
    homepag = "https://github.com/Marcus-Keil/FFT_Benchmark"
    url = "https://github.com/Marcus-Keil/FFT_Benchmark/archive/refs/tags/0.2.tar.gz"

    maintainers("Marcus-Keil")

    version("0.2", sha256="34c9a8c213a78d68c02dedfd998a6909dea32758350871e93235f6875b44e4f8")

    depends_on("c", type="build")
    depends_on("cxx", type="build")

    variant("fftw", default=True, description="FFT Benchmark Base")
    depends_on("fftw", type="link")

    variant("mkl", default=False, description="Enable Intel MKL for FFTW.")
    depends_on("mkl", when="+mkl", type="link")

    variant("cuda", default=False, description="Enable cuFFT Library.")
    depends_on("cuda", when="+cuda", type="link")

    variant("rocfft", default=False, description="Enable rocFFT Library.")
    depends_on("rocfft", when="+rocfft", type="link")

    def cmake_args(self):
        args = [
            self.define("CMAKE_EXE_LINKER_FLAGS", "-fopenmp"),
            self.define_from_variant("ONEAPI", "mkl"),
            self.define_from_variant("CUDA_FFT", "cuda"),
            self.define_from_variant("CUDA_DIR", "cuda"),
            self.define_from_variant("ROC_FFT", "rocfft"),
            self.define_from_variant("ROCM_DIR", "rocfft")
        ]
        return args

    def install(self, spec, prefix):
        src = (os.getcwd()[:os.getcwd().rfind("/")] +
               "/spack-build-" +
               str(spec)[str(spec).find("/")+1:str(spec).find("/")+8] +
               "/FFT_Bench")
        install_path = prefix + "/bin"
        mkdir(install_path)
        install(src, install_path)

