# Profiling tutorial -- !Work in progress!

## Outline

1. Running a benchmark with a profiler
2. Sampling profilers (Nsight & Vtune)
3. Collecting roofline data (advisor-roofline)

## Profilers in excalibur-tests

The `excalibur-tests` framework allows you to run a profiler together with a benchmark application. To do this, you can set the profiler attribute on the command line using the `-S profiler=...` syntax

We support profilers that can be spack installed without a lincense and don't require modifying the source code or the build system. Currently supported values for the profiler attribute are:

- `advisor-roofline`: it produces a roofline model of your program using Intel Advisor;
- `nsight`: it runs the code with the NVIDIA Nsight Systems profiler;
- `vtune`: it runs the code with the Intel VTune profiler.

For more details, see the [User documentation](https://ukri-excalibur.github.io/excalibur-tests/use/)

## Profiling with Nsight

- NVIDIA Nsight Systems is a low-overhead sampling profiler that supports both CPU and GPU applications.
- Supports both x86 and ARM architectures
- We collect `nsys profile --trace=cuda,mpi,nvtx,openmp,osrt,opengl,syscall`

Run Nsight profiling with
```bash
reframe -c path/to/application -r -S profiler=nsight
```

- Spack installs the `nvidia-nsight-systems` package in the background, including the GUI
- The paths to the collected profile data, and to the GUI launcher are written into `rfm_job.out`
- To run the GUI remotely, you need to login with `ssh -X`. It may be slow on a remote system.
- You can (spack) install the GUI locally to view the data.

## Profiling with VTune

- Intel VTune is a low-overhead sampling profiler that supports CPU applications
- Only runs on x86 architectures

Run VTune profiling with
```bash
reframe -c path/to/application -r -S profiler=vtune
```
- Spack installs `intel-oneapi-vtune` package in the background, including the GUI

## Roofline analysis with Advisor

- Intel Advisor is a tool for on-node performance optimisation. It does analysis for efficient Vectorization, Threading, Memory Usage, and Accelerator Offloading
- Since ~2018 it has had support for automated roofline analysis
- Is only supports x86 CPU architecture
- Won't run on the MPI launcher (because it does on-node analysis). In our benchmarks we have to override it. It can run inside an MPI job on a single rank but we don't currently support it, hopefully will be available in the future.

To run on a single MPI rank without `mpirun`, add the following decorated function to the test class
```python
    @run_before('run')
    def replace_launcher(self):
        self.job.launcher = getlauncher('local')()
```

- We collect `advisor -collect roofline`

Run Advisor roofline collection with
```bash
reframe -c path/to/stream -r -S profiler=advisor-roofline
```

- Similar to Nsight, the GUI is installed by Spack but is slow to run remotely.

