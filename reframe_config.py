import os

site_configuration = {
    'systems': [
        {
            'name': 'csd3',
            'descr': 'CSD3',
            'hostnames': ['login-e-[0-9]+'],
            'modules_system': 'tmod32',
            'partitions': [
                {
                    'name': 'skylake',
                    'descr': 'Skylake compute nodes',
                    'scheduler': 'slurm',
                    'launcher': 'mpirun',
                    'access': ['--partition=skylake'],
                    'environs': ['default'],
                    'max_jobs': 64,
                    'processor': {'num_cpus': 32,
                                  'num_cpus_per_core': 2,
                                  'num_sockets': 2,
                                  'num_cpus_per_socket': 16}
                },
                {
                    'name': 'icelake',
                    'descr': 'Icelake compute nodes',
                    'scheduler': 'slurm',
                    'launcher': 'mpirun',
                    'access': ['--partition=icelake'],
                    'environs': ['default'],
                    'max_jobs': 64,
                    'processor': {'num_cpus': 32,
                                  'num_cpus_per_core': 2,
                                  'num_sockets': 2,
                                  'num_cpus_per_socket': 16}
                },
            ]
        },  # end CSD3
        {
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
            'name': 'isambard',
            'descr': 'Cascade Lake nodes of Isambard 2',
            'hostnames': ['login-0[12]'],
            'partitions': [
                {
                    'name': 'cascadelake',
                    'descr': 'Cascadelake computing nodes',
                    'scheduler': 'pbs',
                    'launcher': 'mpirun',
                    'access': ['-q clxq'],
                    'environs': ['default'],
                    'max_jobs': 20,
                },
            ]
        },  # end Isambard Cascadelake
        {
            'name': 'cosma8',
            'descr': 'COSMA',
            'hostnames': ['login[0-9]a.pri.cosma[0-9].alces.network'],
            'modules_system': 'nomod',
            'partitions': [
                {
                    'name': 'compute-node',
                    'descr': 'Compute nodes',
                    'scheduler': 'slurm',
                    'launcher': 'mpirun',
                    'access': ['--partition=cosma8'],
                    'environs': ['default'],
                    'max_jobs': 64,
                    'processor': {'num_cpus': 256,
                                  'num_cpus_per_core': 2,
                                  'num_sockets': 2,
                                  'num_cpus_per_socket': 128}
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
                },
            ]
        },  # end Tesseract
        {
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
            'name': 'dial3',
            'descr': 'DiaL3',
            'hostnames': ['d3-login.*'],
            'partitions': [
                {
                    'name': 'compute-node',
                    'descr': 'Computing nodes',
                    'scheduler': 'slurm',
                    'launcher': 'mpirun',
                    'environs': ['default'],
                    'max_jobs': 16,
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
                        '%(check_job_completion_time)s|reframe %(version)s|'
                        '%(check_info)s|jobid=%(check_jobid)s|'
                        '%(check_perf_var)s=%(check_perf_value)s|'
                        'ref=%(check_perf_ref)s '
                        '(l=%(check_perf_lower_thres)s, '
                        'u=%(check_perf_upper_thres)s)|'
                        '%(check_perf_unit)s'
                    ),
                    'append': True
                }
            ]
        }
    ],
    'schedulers': [
        {
            'name': 'slurm',
            'target_systems': ['tursa'],
            'use_nodes_option': True,
        },
    ],
}
