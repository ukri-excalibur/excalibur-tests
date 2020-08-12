# OpenFOAM

https://openfoam.org/

This runs a semi-official benchmark using a larger version of the motorbike tutorial included with OpenFOAM, documented [here](https://openfoamwiki.net/index.php/Benchmarks). Note that the provided benchmark run script is not used and instead its functionality has been implemented using ReFrame. The benchmark is run on a range of nodes using as many processes as there are physical cores on the nodes. Timings are for the solution phase only, ignoring meshing steps.
