import os

site_configuration = {
    'systems': [
        {
            # https://www.hpc.cam.ac.uk/systems/peta-4
            'name': 'csd3-skylake',
            'descr': 'CSD3 Skylake',
            'hostnames': ['login-e-[0-9]+'],
            'modules_system': 'tmod32',
            'partitions': [
                {
                    'name': 'compute-node',
                    'descr': 'Skylake compute nodes',
                    'scheduler': 'slurm',
                    'launcher': 'mpirun',
                    'access': ['--partition=skylake'],
                    'environs': ['default'],
                    'max_jobs': 64,
                    'processor': {
                        'num_cpus': 32,
                        'num_cpus_per_core': 2,
                        'num_sockets': 2,
                        'num_cpus_per_socket': 16,
                    }
                },
            ]
        },  # end CSD3 Skylake
        {
            # https://www.hpc.cam.ac.uk/systems/peta-4
            'name': 'csd3-icelake',
            'descr': 'CSD3 Icelake',
            'hostnames': ['login-q-[0-9]+'],
            'modules_system': 'tmod4',
            'partitions': [
                {
                    'name': 'compute-node',
                    'descr': 'Icelake compute nodes',
                    'scheduler': 'slurm',
                    'launcher': 'mpirun',
                    'access': ['--partition=icelake'],
                    'environs': ['default', 'intel2020-csd3'],
                    'max_jobs': 64,
                    'processor': {
                        'num_cpus': 76,
                        'num_cpus_per_core': 1,
                        'num_sockets': 2,
                        'num_cpus_per_socket': 38,
                    },
                },
            ]
        },  # end CSD3 Icelake
        {
            # https://www.rc.ucl.ac.uk/docs/Clusters/Myriad/#node-types
            'name': 'myriad',
            'descr': 'Myriad',
            'hostnames': ['login[0-9]+.myriad.ucl.ac.uk'],
            'partitions': [
                {
                    'name': 'compute-node',
                    'descr': 'Computing nodes',
                    'scheduler': 'sge',
                    'launcher': 'mpirun',
                    'environs': ['default'],
                    'max_jobs': 36,
                    'processor': {
                        'num_cpus': 36,
                        'num_cpus_per_core': 1,
                        'num_sockets': 2,
                        'num_cpus_per_socket': 18,
                    },
                    'resources': [
                        {
                            'name': 'mpi',
                            'options': ['-pe mpi {num_slots}']
                        },
                    ]
                },
            ]
        },  # end Myriad
        {
            # https://gw4-isambard.github.io/docs/user-guide/MACS.html
            'name': 'isambard',
            'descr': 'Cascade Lake nodes of Isambard 2',
            'hostnames': ['login-0[12].gw4.metoffice.gov.uk'],
            'partitions': [
                {
                    'name': 'cascadelake',
                    'descr': 'Cascadelake computing nodes',
                    'scheduler': 'pbs',
                    'launcher': 'mpirun',
                    'access': ['-q clxq'],
                    'environs': ['default'],
                    'max_jobs': 20,
                    'processor': {
                        'num_cpus': 40,
                        'num_cpus_per_core': 1,
                        'num_sockets': 2,
                        'num_cpus_per_socket': 20,
                    },
                },
            ]
        },  # end Isambard Cascadelake
        {
            # https://www.dur.ac.uk/icc/cosma/support/cosma8/
            'name': 'cosma8',
            'descr': 'COSMA',
            'hostnames': ['login[0-9][a-z].pri.cosma[0-9].alces.network'],
            'modules_system': 'tmod4',
            'partitions': [
                {
                    'name': 'compute-node',
                    'descr': 'Compute nodes',
                    'scheduler': 'slurm',
                    'launcher': 'mpiexec',
                    'access': ['--partition=cosma8'],
                    'environs': ['default', 'intel20-mpi-durham', 'intel20_u2-mpi-durham', 'intel19-mpi-durham', 'intel19_u3-mpi-durham'],
                    'max_jobs': 64,
                    'processor': {
                        'num_cpus': 256,
                        'num_cpus_per_core': 2,
                        'num_sockets': 2,
                        'num_cpus_per_socket': 128,
                    },
                }
            ]
        },  # end cosma8
        {
            'name': 'github-actions',
            'descr': 'GitHub Actions runner',
            'hostnames': ['fv-az.*'],  # Just to not have '.*'
            'partitions': [
                {
                    'name': 'default',
                    'scheduler': 'local',
                    'launcher': 'mpirun',
                    'environs': ['builtin']
                }
            ]
        },  # End GitHub Actions
        {
            # https://tesseract-dirac.readthedocs.io/en/latest/user-guide/introduction.html
            'name': 'tesseract',
            'descr': 'Extreme Scaling Tesseract',
            'hostnames': ['tesseract-login.*'],
            'partitions': [
                {
                    'name': 'compute-node',
                    'descr': 'Computing nodes',
                    'scheduler': 'pbs',
                    'launcher': 'mpirun',
                    'environs': ['default'],
                    'max_jobs': 16,
                    'processor': {
                        'num_cpus': 24,
                        'num_cpus_per_core': 2,
                        'num_sockets': 2,
                        'num_cpus_per_socket': 12,
                    },
                },
            ]
        },  # end Tesseract
        {
            # https://epcced.github.io/dirac-docs/tursa-user-guide/scheduler/#partitions
            'name': 'tursa',
            'descr': 'Tursa',
            'hostnames': ['tursa-login.*'],
            'partitions': [
                {
                    'name': 'cpu',
                    'descr': 'CPU computing nodes',
                    'scheduler': 'slurm',
                    'launcher': 'mpirun',
                    'access': ['--partition=cpu', '--qos=standard'],
                    'environs': ['default'],
                    'max_jobs': 16,
                    'processor': {
                        'num_cpus': 64,
                        'num_cpus_per_core': 2,
                        'num_sockets': 2,
                        'num_cpus_per_socket': 32,
                    },
                },
                {
                    'name': 'gpu',
                    'descr': 'GPU computing nodes',
                    'scheduler': 'slurm',
                    'launcher': 'mpirun',
                    'access': ['--partition=gpu', '--qos=standard'],
                    'environs': ['default'],
                    'max_jobs': 16,
                },
            ]
        },  # end Tursa
        {
            # https://dial3-docs.dirac.ac.uk/About_dial3/architecture/
            'name': 'dial3',
            'descr': 'Dirac Data Intensive @ Leicester',
            'hostnames': ['d3-login.*'],
            'modules_system': 'lmod',
            'partitions': [
                {
                    'name': 'compute-node',
                    'descr': 'Computing nodes',
                    'scheduler': 'slurm',
                    'launcher': 'mpirun',
                    'environs': ['default', 'intel-oneapi-openmpi-dial3','intel19-mpi-dial3'],
                    'max_jobs': 64,
                    'processor': {
                        'num_cpus': 128,
                        'num_cpus_per_core': 1,
                        'num_sockets': 2,
                        'num_cpus_per_socket': 64,
                    },
                },
            ]
        },  # end DiaL3
        {
            'name': 'generic',
            'descr': 'generic',
            'hostnames': ['.*'],
            'partitions': [
                {
                    'name': 'default',
                    'descr': 'Default system',
                    'scheduler': 'local',
                    'launcher': 'mpirun',
                    'environs': ['default'],
                },
            ]
        },  # end generic
        # < insert new systems here >
    ],
    'environments': [
        {
            # Since we always build with spack, we are not using the compilers in this environment.
            # The compilers spack uses are definied in the spack specs of the reframe config
            # for each app. Nevertheless, we have to define an environment here to make ReFrame happy.
            'name': 'default',
            'cc': 'cc',
            'cxx': 'c++',
            'ftn': 'ftn'
        },
        {
            'name': 'intel20-mpi-durham',
            'modules':['intel_comp/2020','intel_mpi/2020'],
            'cc': 'mpiicc',
            'cxx': 'mpiicpc',
            'ftn': 'mpiifort'
        },
        {
            'name': 'intel20_u2-mpi-durham',
            'modules':['intel_comp/2020-update2','intel_mpi/2020-update2'],
            'cc': 'mpiicc',
            'cxx': 'mpiicpc',
            'ftn': 'mpiifort'
        },
        {
            'name': 'intel19-mpi-durham',
            'modules':['intel_comp/2019','intel_mpi/2019'],
            'cc': 'mpiicc',
            'cxx': 'mpiicpc',
            'ftn': 'mpiifort'
        },
        {
            'name': 'intel19_u3-mpi-durham',
            'modules':['intel_comp/2019-update3','intel_mpi/2019-update3'],
            'cc': 'mpiicc',
            'cxx': 'mpiicpc',
            'ftn': 'mpiifort'
        },
        {
            'name':'intel-oneapi-openmpi-dial3',
            'modules':['intel-oneapi-compilers/2021.2.0','openmpi4/intel/4.0.5'],
            'cc':'mpicc',
            'cxx':'mpicxx',
            'ftn':'mpif90'
        },
        {
            'name': 'intel19-mpi-dial3',
            'modules':['intel-parallel-studio/cluster.2019.5'],
            'cc': 'mpiicc',
            'cxx': 'mpiicpc',
            'ftn': 'mpiifort'
        },
        {
            'name': 'intel2020-csd3',
            'modules': ["intel/compilers/2020.4",
                        "intel/mkl/2020.4",
                        "intel/impi/2020.4/intel",
                        "intel/libs/idb/2020.4",
                        "intel/libs/tbb/2020.4",
                        "intel/libs/ipp/2020.4",
                        "intel/libs/daal/2020.4",
                        "intel/bundles/complib/2020.4"],
            'cc': 'mpiicc',
            'cxx': 'mpiicpc',
            'ftn': 'mpiifort'
        },
    ],
    'logging': [
        {
            'level': 'debug',
            'handlers': [
                {
                    'type': 'stream',
                    'name': 'stdout',
                    'level': 'info',
                    'format': '%(message)s'
                },
                {
                    'type': 'file',
                    'level': 'debug',
                    'format': '[%(asctime)s] %(levelname)s: %(check_info)s: %(message)s',   # noqa: E501
                    'append': False
                }
            ],
            'handlers_perflog': [
                {
                    'type': 'filelog',
                    'prefix': '%(check_system)s/%(check_partition)s',
                    'level': 'info',
                    'format': (
                        '%(check_job_completion_time)s|'
                        'reframe %(version)s|'
                        '%(check_info)s|'
                        'jobid=%(check_jobid)s|'
                        '%(check_perf_var)s=%(check_perf_value)s|'
                        'num_tasks=%(check_num_tasks)s|'
                        'num_cpus_per_task=%(check_num_cpus_per_task)s|'
                        'num_tasks_per_node=%(check_num_tasks_per_node)s|'
                        'ref=%(check_perf_ref)s|'
                        'lower=%(check_perf_lower_thres)s|'
                        'upper=%(check_perf_upper_thres)s|'
                        'units=%(check_perf_unit)s|'
                        'spack_spec=%(check_spack_spec)s'
                    ),
                    'append': True
                }
            ]
        }
    ],
    'schedulers': [
        {
            'name': 'slurm',
            'target_systems': ['tursa', 'cosma8'],
            'use_nodes_option': True,
        },
    ],
}
