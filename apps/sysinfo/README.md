This "application" provides a way to automatically gather and report information about system hardware.

To use:
1. In the ReFrame configuration `reframe_config.py`, add an environment "sysinfo" for the system/parition(s) of interest (see Alaska example).
1. Run:

            reframe/bin/reframe -C reframe_config.py -c apps/sysinfo/ --run

   This will run an mpi job, producing `output/<system>/<partition>/sysinfo/Sysinfo/sysinfo.json` containing hardware information for every node in the partition. Commit this file.
1. The `apps/sysinfo/sysinfo/sysinfo.ipynb` notebook collates and presents this data: navigate to it in a browser, rerun, save and commit it.

