# CASTEP

Performance tests of the material property code [CASTEP](http://www.castep.org/) using CASTEP-provided benchmarks:
- Small benchmark: [TiN](http://www.castep.org/CASTEP/TiN)
  > a 32-atom TiN surface, with an adsorbed H atom and a vacuum gap. There are 8 k-points, so it should scale well to 8 cores; beyond that, it relies on CASTEP's other parallelisation strategies.
- Medium benchmark: [Al3x3](http://www.castep.org/CASTEP/Al3x3)
  > a 270-atom sapphire surface, with a vacuum gap. There are only 2 k-points, so it is a good test of the performance of CASTEP's other parallelisation strategies.
- Large benchmark: [DNA](http://www.castep.org/CASTEP/DNA)
  > a 1356-atom simulation of a DNA strand (poly-A) with counter-ions, in a large simulation box. There is only 1 k-point (the gamma-point), so, like the Crambin test, its parallel performance is reliant on CASTEP's other parallelisation strategies.

(descriptions from the CASTEP [benchmarks page](http://www.castep.org/CASTEP/Benchmarks))

Each benchmark is run on a range of number of nodes, from 1 up to all available. Each run uses as many mpi tasks (processes) per node as there are physical cores.

The following performance variables are captured:
- 'total_time' (s): Total time required for the simulation, as reported by CASTEP
- 'peak_mem' (kB): Peak memory usage, as reported by CASTEP
- 'parallel_efficiency' (%): Parallel efficiency, as reported by CASTEP
- 'runtime_real' (s): Wallclock time reported by `time` for entire MPI program start to finish (i.e. may include additional setup/teardown time not captured in 'total_time').

# Usage

Run using e.g.:
        
    cd hpc-tests
    conda activate hpc-tests
    reframe/bin/reframe -C reframe_config.py -c apps/castep/ --run --performance-report

Run a specific test by appending e.g.:

    --tag Al3x3

