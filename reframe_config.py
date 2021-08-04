import os

site_configuration = {
    'systems': [
        {
            'name': 'csd3',
            'descr': 'CSD3',
            'hostnames': ['login-e-[0-9]+\.data\.cluster'],
            'modules_system': 'tmod32',
            'partitions': [
                {
                    'name': 'login',
                    'descr': 'CSD3 Login nodes',
                    'scheduler': 'local',
                    'launcher': 'local',
                    'environs': ['gnu'],
                },
                {
                    'name': 'compute-node',
                    'descr': 'Compute nodes',
                    'scheduler': 'slurm',
                    'launcher': 'local',
                    'access': ['--account=DIRAC-DO006-CPU', '--partition=skylake'],
                    'environs': ['gnu'],
                    'max_jobs': 64,
                    'variables': [['SPACK_ROOT', os.getenv('SPACK_ROOT')]],
                }
            ]
        },
        {
            'name': 'myriad',
            'descr': 'Myriad',
            'hostnames': ['login[0-9]+\.myriad\.ucl\.ac\.uk'],
            'modules_system': 'tmod',
            'partitions': [
                {
                    'name': 'login',
                    'descr': 'Login nodes',
                    'scheduler': 'local',
                    'launcher': 'local',
                    'environs': ['gnu', 'intel'],
                },
                {
                    'name': 'cn',
                    'descr': 'Computing nodes',
                    'scheduler': 'sge',
                    'launcher': 'mpirun',
                    'environs': ['gnu'],
                    'max_jobs': 64,
                    'variables': [['SPACK_ROOT', os.getenv('SPACK_ROOT')]],
                    'resources': [
                        {
                            'name': 'mpi',
                            'options': ['-pe mpi {num_slots}']
                        },
                    ]
                },
            ]
        },
    ],
    'environments': [
        {
            'name': 'gnu',
            'cc': 'gcc',
            'cxx': 'g++',
            'ftn': 'gfortran'
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
}
