# Bmark_reframe

This repository contains the reframe code to run the the four benchmark codes for Leicester namely: `Ramses`,` Sphng` and `Trove` (Initial matrix generation) and `Trove_pdsyev` (Diagonalisation).

At present, the build step is separate and is not integrated with the Reframe. For building codes, we can use either Spack and its associated settings file or the normal build process using make. Moreover, the source codes are not public and hence they have not been include in this repository.

However, for 3 DiRAC systems namely: 

1. DIaL3 (University of Leicester), 
2. Cosma8 (University of Durham) and,
3. CSD3 Icelake nodes (University of Cambridge),

we have included the executable in the directory `Bmark_reframe/Executables/System_name` where `System_name` can be any of the 3 system names mentioned above.     

We plan to add the instructions to get the SRC code in near future.

### Organisation of the Repository

The repository contains the following directories and files:-

1.  **Additional_Input_Data:-** This folder contains instructions to get the input data required for Ramses. We do not need any other input data for other benchmarks. We cannot include them in the current repository as they are big in size.
2. **Executables:-** This directory contains the binary files or the executable based on the system name. 
3.  **graphing:-** This directory contains the code for post-processing or collection of results from the perflogs directory (contains the performance log and the output we want from the benchmarks).
4. **Readme.md:-** File explaining the directory structure and instructions to run the code.
5. **Settings.py:-** This file contains various environments and module settings which are used by Reframe to generate the submission scripts.
6. **Others:-** All other directories are the apps/benchmarks that we would like to run. Each of the app contains the following files:-
   1. **perflogs:-** Also known as performance logs. This directory contains that output that we get by running the benchmark on a particular system.
   2. **Pyhton code:-** There is one file with extension `.py` which is the reframe code to generate and run the benchmark.
   3. **SRC:-** This is the directory which contains the various inputs for the test cases under consideration. It is this directory where you would need to copy the executable from the `Executable` directory to run the benchmark. Please read the instructions below to know what needs to be copied and where.

### Steps to run a benchmark

1. You would first need to use the settings file that is included in the current repository. This file has been specifically written for Dial3 cluster while the logging format at the end is generic and can be adapted to any system.

   ```bash
   export RFM_CONFIG_FILE=Settings.py
   ```

2. First chose the benchmark you want to run and on which you would like to run. For the sake of explaining, we assume that you want to run `Ramses` on Dial3. You then need to copy the executable  to the `App_name/src` directory where `App_name` can be Ramses, Sphng, Trove or Trove_pdsyey.

   ```bash
   #cp Executables/System_on_which_you_want_to_run/App_name/ramses3d App_name/src/
   cp Executables/Dial3/Ramses/ramses3d Ramses/src/
   ```
   
   In each of the app that you would like to run, you will see a python code (Based on Reframe) in which we defined the executable name. For example, in case on Ramses, you will notice a file `ramses.py` in `Bmark_reframe/Ramses` directory. If you open this file in your favourite editor, you will find the following instruction in the first few lines of the code,
   
   ```python
   self.executable = './ramses3d'
   ```

   Make sure that the executable you copied and the executable name in Python code are same. At present, the files in the `Executable` directory may have different names. This is for our reference as it helps us to know which compiler was used to generate the binary file and which environment we need to choose. 
   
2. Then you can run the three benchmarks by one of the following three commands.

   ```bash
   #***************************************************************************************************
   # Dial 3
   #***************************************************************************************************
   #1. Trove
   reframe -c ./trove.py -r --system dial:slurm-mpirun -p intel19-mpi-dial3 --performance-report
   
   #2. Sphng
   reframe -c ./sphng.py -r --system dial:slurm-mpirun -p intel19-mpi-dial3 --performance-report
   
   #3. Ramses
   reframe -c ./ramses.py -r --system dial:slurm-mpirun -p intel-oneapi-openmpi-dial3 --performance-report
   
   #. Trove_pdsyev (Crrently tested on Dial3 only)
   reframe -c ./pdsyev.py -r --system dial:slurm-mpirun -p intel19-mpi-dial3 --performance-report
   
   #***************************************************************************************************
   # Cosma8
   #***************************************************************************************************
   #1. Trove
   reframe -c ./trove.py -r --system cosma8:compute-node -p intel19_u3-mpi-durham --performance-report
   
   #2. Sphng
   reframe -c ./sphng.py -r --system cosma8:compute-node -p intel20_u2-mpi-durham --performance-report
   
   #3. Ramses
   reframe -c ./ramses.py -r --system cosma8:compute-node -p intel20-mpi-durham --performance-report
   
   #***************************************************************************************************
   # Csd3
   #***************************************************************************************************
   ```
   
   If you would like to keep all the stage files (intermediate files during the run), add the lag `--keep-stage-files` at the end of the command.
   
   For example, if you plan to run Ramses and want to keep the stage files, you would use the following command.
   
   ```bash
   reframe -c ./ramses.py -r --system dial:slurm-mpirun -p intel-oneapi-openmpi-dial3 --performance-report --keep-stage-files
   ```
   
   If instead of running the complete benchmark, you want to run only a part of it, you can use the Tags that have been defined in the respective Pyhton files. For example, to run the `12N` case for Trove on Cosma8, you can use the following command.
   
   ```bash
    reframe -c ./trove.py -r --system cosma8:compute-node -p intel19_u3-mpi-durham --performance-report --keep-stage-files --tag="12N"
   ```

Note:- Since the benchmarks take good enough time to run and they may be in the queue for a long time, we suggest to use a method by which you can restore your SSH session such as by using `tmux`.

### Steps to visualise the data

To generate a pdf report including the benchmarks.

   ```bash
   cd graphing && make
   ```

Note:- Latex and Python are required + the Python requirements (`graphing/requirements.txt`).

### Acknowledgement

We would like to kindly acknowledge the help we received from Kiril Dichev, HPC Consultant, University of Cambridge for providing the reframe code for the Trove_pdsyev benchmark. At present, the repository uses a modified version of what we received from Kiril.
