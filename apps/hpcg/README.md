# High Performance Conjugate Gradient - Intel-optimised version

This runs an Intel version of the High Performance Conjugate Gradient Benchmark optimised for Intel Xeon processors and linked against using Intel's MKL.

Documentation is [here](https://software.intel.com/content/www/us/en/develop/documentation/mkl-linux-developer-guide/top/intel-math-kernel-library-benchmarks/intel-optimized-high-performance-conjugate-gradient-benchmark/overview-of-the-intel-optimized-hpcg.html)

It follows recommendations for performance given in [Intel docs](https://software.intel.com/content/www/us/en/develop/documentation/mkl-linux-developer-guide/top/intel-math-kernel-library-benchmarks/intel-optimized-high-performance-conjugate-gradient-benchmark/choosing-best-configuration-and-problem-sizes.html)

# Installation of Intel-HPL using Spack

Prebuilt binaries are provided with MKL - tests here use AVX2-specific binaries so assume system is AVX2-capable.

E.g.:

    spack load patch
    spack load gcc@9
    spack install intel-mpi %gcc@9: # DONE
    spack install intel-mkl %gcc@9: # NB this doesn't have threads enabled here/by default

Note that the executables are provided within the MKL installation directory, e.g.:

    $HOME/spack/opt/spack/linux-centos7-broadwell/gcc-9.3.0/intel-mkl-2020.1.217-5tpgp7bze633d4bybvvumfp2nhyg64xf/compilers_and_libraries_2020.1.217/linux/mkl/benchmarks/hpcg/bin/

which contains:

    hpcg.dat    xhpcg_avx   xhpcg_avx2  xhpcg_knl   xhpcg_skx

The ReFrame environment configuration(s) for this test **must** include two items:

Firstly, to add the `/bin` directory to $PATH (as the spack-generated MKL module does not do this) include:
    
    ['PATH', '$PATH:$MKLROOT/benchmarks/hpcg/bin/']
    
(Note that `MKLROOT` is exported by the MKL module).

Secondly, to select the appropriate binary for the system include:

    ['XHPCG_BIN', <binary>]

where `<binary>` is one of the above - note `xhpcg_skx` is AVX512 (Skylake).

# hpcg .dat configuration files

Appropriate HPCG configuration files named `hpcg-single.dat` and `hpcg-all.dat` for the single- and all-node cases respectively must be generated and placed in either:

- `<repo_root>/systems/<sysname>/hpl/`
- `<repo_root>/systems/<sysname>/<partition>/hpl/`

Note that an example file is provided in the binary directory described above.

# Running tests

Requires AVX2

# Outputs