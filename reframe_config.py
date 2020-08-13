site_configuration = {
    'systems': [
        {
            'name':'alaska',
            'descr':'Default AlaSKA OpenHPC p3-appliances slurm cluster',
            'hostnames': ['openhpc-login-0', 'openhpc-compute'],
            'modules_system':'lmod',
            'partitions':[
                # system compiler+mpi:
                {
                    'name':'ib-gcc7-openmpi3-openib',
                    'descr': '100Gb Infiniband with gcc 7.3.0 and openmpi 3.1.0 using openib transport layer',
                    'scheduler': 'slurm',
                    'launcher':'srun',
                    'environs': ['imb'],
                    'modules':['gnu7','openmpi3'],
                    'variables':[
                        # Use pmix to launch parallel applications - equivalent to `srun --mpi=pmix_v2`
                        ['SLURM_MPI_TYPE', 'pmix_v2'],

                        # For openib btl
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
                    'name':'roce-gcc7-openmpi3-openib',
                    'descr': '25Gb RoCE with gcc 7.3.0 and openmpi 3.1.0 using openib transport layer',
                    'scheduler': 'slurm',
                    'launcher':'srun',
                    'max_jobs':8,
                    'environs': ['imb'],
                    'modules': ['gnu7','openmpi3'],
                    'variables': [
                        # Use pmix to launch parallel applications - equivalent to `srun --mpi=pmix_v2`
                        ['SLURM_MPI_TYPE', 'pmix_v2'],

                        ['OMPI_MCA_btl', 'openib,self,vader'],
                        ['OMPI_MCA_btl_openib_if_include', 'mlx5_1:1'],
                        # Set receive queues. From https://community.mellanox.com/s/article/howto-configure-ib-routers:
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
                # system compiler, spack mpi:
                {
                    'name':'ib-gcc7-openmpi4-ucx',
                    'descr': '100Gb Infiniband with gcc 7.3.0 and openmpi 4.0.3 using UCX transport layer',
                    'scheduler': 'slurm',
                    'launcher':'srun',
                    'max_jobs':8,
                    'environs': ['imb', 'gromacs', 'omb', 'hpl', 'openfoam', 'cp2k'],
                    'modules': ['openmpi/4.0.3-ziwdzwh'],
                    'variables': [
                        # Use pmix to launch parallel applications - equivalent to `srun --mpi=pmix_v2`
                        ['SLURM_MPI_TYPE', 'pmix_v2'],

                        # (no vars required for ucx on ib - fastest CA available)
                    ]
                },
                {
                    'name':'roce-gcc7-openmpi4-ucx',
                    'descr': '25Gb RoCE with gcc 7.3.0 and openmpi 4.0.3 using UCX transport layer',
                    'scheduler': 'slurm',
                    'launcher':'srun',
                    'environs': ['imb', 'gromacs', 'omb', 'hpl', 'openfoam', 'cp2k'],
                    'modules': ['openmpi/4.0.3-ziwdzwh'],
                    'variables': [
                        # Use pmix to launch parallel applications - equivalent to `srun --mpi=pmix_v2`
                        ['SLURM_MPI_TYPE', 'pmix_v2'],
                        # use roce:
                        ['UCX_NET_DEVICES', 'mlx5_1:1'],
                    ]
                },
                # intel mpi:
                {
                    'name':'ib-gcc9-impi-verbs',
                    'descr': '100Gb Infiniband with gcc 9.3.0 and Intel MPI 2019.7.217',
                    'scheduler': 'slurm',
                    'launcher':'mpirun',
                    'max_jobs':8,
                    'environs': ['imb', 'omb', 'intel-hpl', 'intel-hpcg'],
                    'modules': ['gcc/9.3.0-5abm3xg', 'intel-mpi/2019.7.217-bzs5ocr'],
                    'variables': [
                        #['FI_PROVIDER', 'mlx'] # doesn't work, needs ucx
                        ['FI_VERBS_IFACE', 'ib'] # # Network interface to use - this is actually default
                        # these were (failed) attempts to make `srun` work:
                        #['I_MPI_PMI_LIBRARY', '/opt/ohpc/admin/pmix/lib/libpmi.so'], # see https://slurm.schedmd.com/mpi_guide.html#intel_mpi
                        #['SLURM_MPI_TYPE', 'pmi2'],
                    ],
                },
                {
                    'name':'roce-gcc9-impi-verbs',
                    'descr': '25Gb RoCE with gcc 9.3.0 and Intel MPI 2019.7.217 using verbs',
                    'scheduler': 'slurm',
                    'launcher':'mpirun',
                    'max_jobs':8,
                    'environs': ['imb', 'omb', 'intel-hpl', 'intel-hpcg'],
                    'modules': ['gcc/9.3.0-5abm3xg', 'intel-mpi/2019.7.217-bzs5ocr'],
                    'variables': [
                        ['FI_VERBS_IFACE', 'p3p2'] # Network interface to use.
                    ],
                },
                # latest working gcc:
                {
                    'name':'ib-gcc9-openmpi4-ucx',
                    'descr':'100Gb Infiniband with gcc 9.3.0 and openmpi 4.0.3 using UCX transport layer',
                    'scheduler': 'slurm',
                    'launcher':'srun',
                    'max_jobs':8,
                    'environs':['imb', 'omb', 'gromacs', 'openfoam', 'cp2k'],
                    'modules': ['gcc/9.3.0-5abm3xg', 'openmpi/4.0.3-qpsxmnc'],
                    'variables': [
                        ['SLURM_MPI_TYPE', 'pmix_v2'],
                    ]
                },
                {
                    'name':'roce-gcc9-openmpi4-ucx',
                    'descr':'25Gb RoCE with gcc 9.3.0 and openmpi 4.0.3 using UCX transport layer',
                    'scheduler': 'slurm',
                    'launcher':'srun',
                    'max_jobs':8,
                    'environs':['imb', 'omb', 'gromacs', 'openfoam', 'cp2k'],
                    'modules': ['gcc/9.3.0-5abm3xg', 'openmpi/4.0.3-qpsxmnc'],
                    'variables': [
                        ['SLURM_MPI_TYPE', 'pmix_v2'],
                        # use roce:
                        ['UCX_NET_DEVICES', 'mlx5_1:1'],
                    ]
                },
            ]
        }, # end alaska
        # < insert new systems here >
    ],
    'environments': [
        {
            'name': 'imb',      # a non-targeted environment seems to be necessary for reframe to load the config
        },
        {
            'name': 'imb', # OHPC-provided packages
            'target_systems': ['alaska:ib-gcc7-openmpi3-openib', 'alaska:roce-gcc7-openmpi3-openib'],
            'modules': ['imb'],
        },
        {
            'name': 'imb', # spack-provided packages
            'target_systems': ['alaska:ib-gcc7-openmpi4-ucx', 'alaska:roce-gcc7-openmpi4-ucx'],
            'modules': ['intel-mpi-benchmarks/2019.5-q5ujyli'],
        },
        {
            'name': 'imb', # spack-provided packages
            'target_systems': ['alaska:ib-gcc9-openmpi4-ucx', 'alaska:roce-gcc9-openmpi4-ucx'],
            'modules': ['intel-mpi-benchmarks/2019.5-dwg5q6j'],
        },
        {
            'name': 'imb', # spack-provided packages
            'target_systems': ['ib-gcc9-impi-verbs', 'roce-gcc9-impi-verbs'],
            'modules': ['intel-mpi-benchmarks/2019.5-w54huiw'],
        },
        {
            'name': 'gromacs',
        },
        {
            'name': 'gromacs',
            'target_systems': ['alaska:ib-gcc7-openmpi4-ucx', 'alaska:roce-gcc7-openmpi4-ucx'],
            'modules': ['gromacs/2016.4-xixmrii']
        },
        {
            'name': 'gromacs',
            'target_systems': ['alaska:ib-gcc9-openmpi4-ucx', 'alaska:roce-gcc9-openmpi4-ucx'],
            'modules': ['gromacs/2016.4-y5sjbs4']
        },
        {
            'name': 'omb',
        },
        {
            'name': 'omb',
            'target_systems': ['alaska:ib-gcc7-openmpi4-ucx', 'alaska:roce-gcc7-openmpi4-ucx'],
            'modules': ['osu-micro-benchmarks/5.6.2-el6z55i']
        },
        {
            'name': 'omb',
            'target_systems': ['alaska:ib-gcc9-openmpi4-ucx', 'alaska:roce-gcc9-openmpi4-ucx'],
            'modules': ['osu-micro-benchmarks/5.6.2-vx3wtzo']
        },
        {
            'name': 'omb',
            'target_systems': ['alaska:ib-gcc9-impi-verbs', 'alaska:roce-gcc9-impi-verbs'],
            'modules': ['osu-micro-benchmarks/5.6.2-ppxiddg']
        },
        {
            'name': 'hpl',
        },
        {
            'name': 'hpl',
            'target_systems': ['alaska:ib-gcc7-openmpi4-ucx', 'alaska:roce-gcc7-openmpi4-ucx'],
            'modules': ['hpl/2.3-tgk5uqq'],
        },
        {
            'name': 'intel-hpl',
        },
        {
            'name': 'intel-hpl',
            'target_systems': ['alaska:ib-gcc9-impi-verbs', 'alaska:roce-gcc9-impi-verbs'],
            'modules': ['intel-mkl/2020.1.217-5tpgp7b'],
            'variables':[
                ['PATH', '$PATH:$MKLROOT/benchmarks/mp_linpack/'], # MKLROOT provided by mkl module
            ],
        },
        {
            'name': 'intel-hpcg',
        },
        {
            'name': 'intel-hpcg',
            'target_systems': ['alaska:ib-gcc9-impi-verbs', 'alaska:roce-gcc9-impi-verbs'],
            'modules': ['intel-mkl/2020.1.217-5tpgp7b'],
            'variables':[
                ['PATH', '$PATH:$MKLROOT/benchmarks/hpcg/bin/'], # MKLROOT provided by mkl module
                ['XHPCG_BIN', 'xhpcg_avx2'],
                ['SLURM_CPU_BIND', 'verbose'], # doesn't work as task/affinity plugin not enabled
            ]
        },
        {
            'name':'openfoam'
        },
        {
            'name':'openfoam',
            'target_systems': ['alaska:ib-gcc7-openmpi4-ucx', 'alaska:roce-gcc7-openmpi4-ucx'],
            'modules': ['openfoam-org/7-2ceqb4l']
        },
        {
            'name':'openfoam',
            'target_systems': ['alaska:ib-gcc9-openmpi4-ucx', 'alaska:roce-gcc9-openmpi4-ucx'],
            'modules': ['openfoam-org/7-4zgjbg2']
        },
        {
            'name':'cp2k',
        },
        {
            'name':'cp2k',
            'target_systems': ['alaska:ib-gcc7-openmpi4-ucx', 'alaska:roce-gcc7-openmpi4-ucx'],
            'modules': ['cp2k/7.1-spcqy4k']
        },
        {
            'name':'cp2k',
            'target_systems': ['alaska:ib-gcc9-openmpi4-ucx', 'alaska:roce-gcc9-openmpi4-ucx'],
            'modules': ['cp2k/7.1-akb54dx']
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
                    'format': '%(check_job_completion_time)s|reframe %(version)s|%(check_info)s|jobid=%(check_jobid)s|%(check_perf_var)s=%(check_perf_value)s|%(check_perf_unit)s|ref=%(check_perf_ref)s (l=%(check_perf_lower_thres)s, u=%(check_perf_upper_thres)s)|%(check_tags)s',  # noqa: E501
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
