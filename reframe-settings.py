site_configuration = {
    'systems': [
        {
            'name':'sausage-newslurm',
            'descr': "sausagecloud newslurm cluster",
            'hostnames': ['steveb-newslurm-control-0', 'steveb-newslurm-compute'],
            'modules_system': 'lmod',
            'partitions': [
                {
                    'name':'compute',
                    'scheduler': 'slurm',
                    'launcher':'mpirun',
                    'environs': ['gnu-openmpi',],
                }
            ]
        },
        {
            'name':'alaska',
            'descr':'Default AlaSKA OpenHPC p3-appliances slurm cluster',
            'hostnames': ['openhpc-login-0', 'openhpc-compute'],
            'modules_system':'lmod',
            'partitions':[
                {
                    'name':'compute-ib',
                    'scheduler': 'slurm',
                    'launcher':'mpirun',
                    'environs': ['gnu-openmpi',],
                    'variables':[
                        ['OMPI_MCA_btl', 'openib,self,vader'],
                        ['OMPI_MCA_btl_openib_if_include', 'mlx5_0:1'],
                        # TODO: find a way to add --bind-to core option
                    ]
                },
                {
                    'name':'compute-roce',
                    'scheduler': 'slurm',
                    'launcher':'mpirun',
                    'environs': ['gnu-openmpi',],
                    'variables':[
                        ['OMPI_MCA_btl', 'openib,self,vader'],
                        ['OMPI_MCA_btl_openib_if_include', 'mlx5_1:1'],
                    ]
                }
            ]
        }
    ],
    'environments': [
        {
            'name':'gnu-openmpi',
            'target_systems': ['sausage-newslurm',],
            'modules': ['gnu8', 'openmpi3'],
        },
        {
            'name':'gnu-openmpi',
            'target_systems': ['alaska',],
            #'modules': ['gnu7', 'openmpi3'], # OHPC-provided
            'modules': ['gcc/8.3.0-znuxkla', 'openmpi/3.1.6-h4l75yo']
        },
    ],
    'logging': [
        {
            'level': 'debug',
            'handlers': [
                {
                    'type': 'file',
                    'name': 'reframe.log',
                    'level': 'debug',
                    'format': '[%(asctime)s] %(levelname)s: %(check_name)s: %(message)s',   # noqa: E501
                    'append': False
                },
                {
                    'type': 'stream',
                    'name': 'stdout',
                    'level': 'info',
                    'format': '%(message)s'
                },
                {
                    'type': 'file',
                    'name': 'reframe.out',
                    'level': 'info',
                    'format': '%(message)s',
                    'append': False
                }
            ],
            'handlers_perflog': [
                {
                    'type': 'filelog',
                    'prefix': '%(check_system)s/%(check_partition)s',
                    'level': 'info',
                    'format': '%(check_job_completion_time)s|reframe %(version)s|%(check_info)s|jobid=%(check_jobid)s|%(check_perf_var)s=%(check_perf_value)s|ref=%(check_perf_ref)s (l=%(check_perf_lower_thres)s, u=%(check_perf_upper_thres)s)',  # noqa: E501
                    'datefmt': '%FT%T%:z',
                    'append': True
                }
            ]
        }
    ],
    'general': [
        {
            'check_search_path': ['./'],
            'check_search_recursive': True
        }
    ]    
}
