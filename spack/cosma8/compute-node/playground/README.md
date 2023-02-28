# HOW I DID IT

1. Got a list of compiler modules and mpi modules
   using `module av`, aptly edited
2. Invoke `scanner.sh` to scan the cartesian product
   of compilers and mpi modules,
   to find the combinations that load withou errors
3. Save that into a file `all_combinations.txt`, adding a column
   specifying which module spack should look for
4. launch `setup_cosma8.sh`, which loads the combination of modules
   specified in each line of `all_combinations.txt`
   searching for compilers and external mpi installation

Not all is found, e.g., intel mpi packages.
The scripts in this directory
are provided for documentation purposes,
they are not supposed to work out of the box.
