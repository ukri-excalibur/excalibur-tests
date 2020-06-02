#!/usr/bin/env python

import subprocess, time, os
from pprint import pprint
from collections import namedtuple

ResultsKey = namedtuple('ResultsKey', ('metric', 'installer', 'commframe', 'net', 'launcher'))


SBATCH_OPTS = {
    'ntasks':2,
    'ntasks-per-node':1,
    'exclusive':None,
    'output':'%x.out',
}

OMPI_OPENIB_ROCE_QUEUES="--mca btl_openib_receive_queues P,128,64,32,32,32:S,2048,1024,128,32:S,12288,1024,128,32:S,65536,1024,128,32"

RUNS = {
    # installer, "fabric", network, launcher
    # 'ohpc,openib,ib,mpirun': {
    #     'module': ['gnu7', 'openmpi3', 'imb'],
    #     'cmd': 'OMPI_MCA_btl=openib,self,vader OMPI_MCA_btl_openib_if_include=mlx5_0:1 mpirun IMB-MPI1 pingpong',
    # },
    # 'ohpc,openib,ib,srun': {
    #     'module': ['gnu7', 'openmpi3', 'imb'],
    #     'cmd': 'OMPI_MCA_btl=openib,self,vader OMPI_MCA_btl_openib_if_include=mlx5_0:1 srun --mpi=pmix_v2 IMB-MPI1 pingpong',
    # },
    'ohpc,openib,roce,mpirun': {
        'module': ['gnu7', 'openmpi3', 'imb'],
        'cmd': 'OMPI_MCA_btl=openib,self,vader OMPI_MCA_btl_openib_if_include=mlx5_1:1 mpirun %s IMB-MPI1 pingpong' % OMPI_OPENIB_ROCE_QUEUES,
    },
    # 'spack,ucx,ib,orterun':{
    #     'spack': ['intel-mpi-benchmarks@2019.5'],
    #     'cmd':'orterun IMB-MPI1 pingpong',
    # },
    # 'spack,ucx,roce,orterun':{
    #     'spack':['intel-mpi-benchmarks@2019.5'],
    #     'cmd':'orterun --mca pml ucx -x UCX_NET_DEVICES=mlx5_1:1 IMB-MPI1 pingpong',
    # },
    'spack,ucx,ib,srun':{
        'spack':['/q5ujyli'], # intel mpi benchmarks using openmpi 4.0.3 with scheduler=auto and ucx
        #'cmd':'srun --mpi=pmix_v2 --mca pml ucx -x UCX_NET_DEVICES=mlx5_0:1 IMB-MPI1 pingpong',
        'cmd':'srun --mpi=pmix_v2 IMB-MPI1 pingpong',
    },
    'spack,ucx,roce,srun':{
        'spack':['/q5ujyli'], # intel mpi benchmarks using openmpi 4.0.3 with scheduler=auto and ucx
        'cmd':'UCX_NET_DEVICES=mlx5_1:1 srun --mpi=pmix_v2 IMB-MPI1 pingpong',
    },
}

def write_script():

    scripts = []
    for run in RUNS:
        runscript = run.replace(',','-') + '.sh'
        with open(runscript, 'w') as f:
            f.write('#!/usr/bin/bash\n')
            for k, v in SBATCH_OPTS.items():
                if v is not None:
                    f.write('#SBATCH --%s=%s\n' % (k, v))
                else:
                    f.write('#SBATCH --%s\n' % k)
            for module in RUNS[run].get('module', []):
                f.write('module load %s\n' % module)
            for pkg in RUNS[run].get('spack', []):
                f.write('spack load %s\n' % pkg)
            f.write('%s\n' % RUNS[run]['cmd'])
        scripts.append(runscript)
    return scripts

def launch_scripts(scripts):
    jobids = []
    for s in scripts:
        sbatch = subprocess.run(['sbatch', s], capture_output=True, text=True)
        if sbatch.stderr:
            raise ValueError('%s stderr: %s' % (s, sbatch.stderr))
        jobid = sbatch.stdout.strip().split()[-1]
        jobids.append(jobid)
    return jobids

def read_imb_out(path):
    """ Read stdout from an IMB-MPI1 run. Note this may only contain ONE benchmark.
        
        Returns a dict with keys:
            
            'data': {
                    <column_heading1>: [value0, value1, ...],
                    ...,
                }
            'meta':
                'processes':num processes as int
                'benchmark': str, as above
                'path': str
    
        TODO: use numpy instead?
    """

    COLTYPES = {
        'uniband':(int, int, float, int),
        'biband':(int, int, float, int),
        'pingpong':(int, int, float, float),
    }

    result = {
        'meta': {},
        'data': {},
        }
    with open(path) as f:
        for line in f:
            if line.startswith('# Benchmarking '):
                benchmark = line.split()[-1].lower()
                if 'benchmark' in result['meta']:
                    raise ValueError('%s may only contain one benchmark, found both %r and %r' % (result['meta']['benchmark'], benchmark))
                result['meta']['benchmark'] = benchmark
                col_types = COLTYPES[benchmark]
                result['meta']['processes'] = int(next(f).split()[-1]) # "# #processes = 2"
                next(f) # skip header
                while True:
                    cols = next(f).split()
                    if cols == []:
                        break
                    if cols[0].startswith('#'): # header row
                        header = cols
                        for label in header:
                            result['data'][label] = []
                    else:
                        for label, opr, value in zip(header, col_types, cols):
                            result['data'][label].append(opr(value))
    return result

def wait_for_jobs(job_ids, delay=5):
    while True:
        squeue = subprocess.run(['squeue', '--jobs=%s' % ','.join(job_ids), '--noheader'], capture_output=True, text=True)
        stdout = squeue.stdout.strip()
        if squeue.stdout == '':
            #print('continuing')
            break
        else:
            queued_jobids = [s.split()[0] for s in stdout.split('\n')]
            print('waiting for jobs %s' % ', '.join(queued_jobids))
            time.sleep(delay)

METRICS = [ # name, column, function, unit
    ('max bandwidth', 'Mbytes/sec', max, 'Mbytes/s'),
    ('min latency', 't[usec]', min, 'us'),
]

def where(mapping, **kwargs):
    output = {}
    for k, v in mapping.items():
        matches = [True if u == getattr(k, p) else False for p, u in kwargs.items()]
        if all(matches):
            output[k] = v
    return output

def group(mapping, attr):
    output = {}
    for key, value in mapping.items():
        partialkey = getattr(key, attr)
        curr = output.setdefault(partialkey, {})
        curr[key] = value
    return output

if __name__ == '__main__':
    scripts = write_script()
    jobids = launch_scripts(scripts)
    wait_for_jobs(jobids)

    results = {}
    for script in scripts:
        try:
            outpath = '%s.out' % script
            output = read_imb_out(outpath)
            for metric in METRICS:
                metricname, col, func, unit = metric
                value = func(output['data'][col])
                installer, commframe, net, launcher = script.split('.')[0].split('-') # commframe = btl or pml
                key = ResultsKey(metricname, installer, commframe, net, launcher)
                results[key] = (value, unit)
        except Exception:
            print('ERROR: while processing %s' % os.path.abspath(outpath))
            raise

    #results = group(results, 'metric')
    pprint(results)
        

        