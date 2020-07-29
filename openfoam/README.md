# OpenFOAM

https://openfoam.org/

This runs the motorbike tutorial included with OpenFOAM on a range of number of nodes. Timings are reported for the completion of the tutorial-provided wrapper script, `Allrun`. Note that this runs pre- and post-processing applications as well as the actual solver, not all of which are parallelised.

Parallel parts of a run use as many processes as there are physical cores on the nodes.