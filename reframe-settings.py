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
                    'name':'compute-ib-openib',
                    'scheduler': 'slurm',
                    'launcher':'srun',
                    'environs': ['ohpc-gnu7-openmpi3'],
                    'variables':[
                        # Use pmix to launch parallel applications - equivalent to `srun --mpi=pmix_v2`
                        ['SLURM_MPI_TYPE', 'pmix_v2'],

                        # For openmpi btl
                        # ---------------
                        ['OMPI_MCA_btl', 'openib,self,vader'],
                        ['OMPI_MCA_btl_openib_if_include', 'mlx5_0:1'],
                        # note that --bind-to core is actually the default for ompi 3.1. Tried setting it manually here using:
                        ['OMPI_MCA_hwloc_base_binding_policy', 'core'],
                        # as JT was using this, but:
                        # - was higher latency for imb pingping (1.58us vs 1.32us without)
                        # - showed no difference in --report-bindings!
                        # can also use "hwthread" but this is slower still.
                    ]
                },
                {
                    'name':'compute-ib-ucx',
                    'scheduler': 'slurm',
                    'launcher':'srun',
                    'environs': ['spack-gnu7-openmpi4'],
                    'variables':[
                        # Use pmix to launch parallel applications - equivalent to `srun --mpi=pmix_v2`
                        ['SLURM_MPI_TYPE', 'pmix_v2'],

                        # (no vars required for ucx on ib - fastest CA available)
                    ]
                },
                {
                    'name':'compute-roce-openib',
                    'scheduler': 'slurm',
                    'launcher':'srun',
                    'environs': ['ohpc-gnu7-openmpi3'],
                    'variables':[
                        # Use pmix to launch parallel applications - equivalent to `srun --mpi=pmix_v2`
                        ['SLURM_MPI_TYPE', 'pmix_v2'],

                        ['OMPI_MCA_btl', 'openib,self,vader'],
                        ['OMPI_MCA_btl_openib_if_include', 'mlx5_1:1'],
                        # Set recieve queues. From https://community.mellanox.com/s/article/howto-configure-ib-routers:
                        # > In order for you to use rdmacm, you must set up a per-peer QP as the first QP (all QPs cannot be SRQ).
                        #   In some branches of ompi, the default is to use only SRQ. In this case, add -mca btl_openib_receive_queues P,65536,256,192,128 to the command line.
                        #   In the current v1.10 branch, the default configuration should work with IB routing without any changes.
                        # Note that `receive_queues` is not specified for ConnectX4 in $MPI_DIR/share/openmpi/mca-btl-openib-device-params.ini, so we have to set it at runtime:
                        ['OMPI_MCA_btl_openib_receive_queues',
                            #'P,65536,256,192,128'], # From above mellanox link, minimal case
                            #'P,65536,256,192,128:S,128,256,192,128:S,2048,1024,1008,64:S,12288,1024,1008,64:S,65536,1024,1008,64' # From above mellanox link, described as optimal for osu_bw:
                            'P,128,64,32,32,32:S,2048,1024,128,32:S,12288,1024,128,32:S,65536,1024,128,32' # From John Taylor (source unknown) - this appears to be lower latency for pingpong
                        ],
                    ]
                },
                {
                    'name':'compute-roce-ucx',
                    'scheduler': 'slurm',
                    'launcher':'srun',
                    'environs': ['spack-gnu7-openmpi4'],
                    'variables':[
                        # Use pmix to launch parallel applications - equivalent to `srun --mpi=pmix_v2`
                        ['SLURM_MPI_TYPE', 'pmix_v2'],

                        ['UCX_NET_DEVICES', 'mlx5_1:1'],
                    ]
                }
            ]
        }
    ],
    'environments': [
        {
            'name':'gnu-openmpi',
            'target_systems': ['sausage-newslurm',],
            'modules': ['gnu8', 'openmpi3',],
        },
        {
            'name':'ohpc-gnu7-openmpi3', # OHPC-provided packages
            'target_systems': ['alaska',],
            'modules': [
                'gnu7',
                'openmpi3',
                'imb',
            ],
        },
        {
            'name':'spack-gnu7-openmpi4', # spack-provided packages
            'target_systems': ['alaska',],
            'modules': [
                'openmpi/4.0.3-ziwdzwh',
                'intel-mpi-benchmarks/2019.5-q5ujyli',
                'gromacs/2016.4-xixmrii',
            ],
        }
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
                    # make this the same as output filenames which are ('sysname', 'partition', 'environ', 'testname', 'filename')
                    'prefix': '%(check_system)s/%(check_partition)s/%(check_environ)s/%(check_name)s', # <testname>.log gets appended
                    'level': 'info',
                    # added units here - see Reference: https://reframe-hpc.readthedocs.io/en/latest/config_reference.html?highlight=perflog#logging-.handlers_perflog
                    'format': '%(check_job_completion_time)s|reframe %(version)s|%(check_info)s|jobid=%(check_jobid)s|%(check_perf_var)s=%(check_perf_value)s|%(check_perf_unit)s|ref=%(check_perf_ref)s (l=%(check_perf_lower_thres)s, u=%(check_perf_upper_thres)s)',  # noqa: E501
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
