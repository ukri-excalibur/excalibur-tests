# OpenFOAM

Performance tests of the computational fluid dynamics package Openfoam https://openfoam.org/ using a larger version of the motorbike tutorial included with OpenFOAM, as documented [here](https://openfoamwiki.net/index.php/Benchmarks).

The benchmark is run on a range of number of nodes, from 1 up to all available. Each run uses as many processes per node as there are physical cores.

The following performance variables are captured:
- 'ExecutionTime' (s): TODO: Clarify what this actually calculates.
- 'ClockTime' (s): Wallclock time as reported by Openfoam.
- 'runtime_real' (s): Wallclock time reported by `time` for entire MPI program start to finish.

All these timings are for the solver run only, ignoring meshing etc.

# Installing using spack

E.g.:

    spack install openfoam-org %gcc@7.3.0 ^/ziwdzwh

See main README for comments on MPI libraries.

# Usage

Run using e.g.:

    reframe/bin/reframe -C reframe_config.py -c openfoam/ --run --performance-report

Run on a specific number of nodes by appending:

    --tag 'N$'

where N must be one of 1, 2, 4, ..., etc.