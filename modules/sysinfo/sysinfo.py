#!/usr/bin/env python
""" Get performance-related information about host hardware.

    Usage:
        sysinfo.py
        sysinfo.py sysname file0 ... fileN
    
    The first form retrieves information about the current host and saves it in a file `$HOSTNAME.sysinfo.json`.
    The second form collates information from multiple host data files and saves it in a file SYSNAME.sysinfo.json.

    It requires the following shell commands to be available:
    - lscpu
    - lspci
    - free
    
    Root should not be required.

    Creates a file `$HOSTNAME.sysinfo.json`.
"""

import subprocess, pprint, collections, os, glob, socket, json, sys

def merge(dicts, path=None):
    """ Merge a sequence of nested dicts into a single nested dict.

        Input dicts must contain the same keys and the same type of values at each level.

        For each (nested) key, if all input dicts have the same value, the output dict will have a single value.
        If not, the output dict will have a list of values, in the same order as the input dicts.
    """
    if path is None:
        path = []
    result = {}
    for key in dicts[0]:
        vals = [d[key] for d in dicts]
        if len(vals) != (len(dicts)):
            raise ValueError('At least one dict is missing key at %s' % '.'.join(path + [str(key)]))
        elif len(set(type(v) for v in vals)) > 1:
            raise ValueError('More than one type of value for key at %s' % '.'.join(path + [str(key)]))
        elif isinstance(vals[0], dict):
            result[key] = merge(vals, path + [str(key)])
        else:
            if isinstance(vals[0], list):
                vals = [tuple(v) for v in vals]
            unique_vals = set(vals)
            if len(unique_vals) == 1:
                result[key] = vals[0]
            else:
                result[key] = vals
    return result

def read_file(path, default=''):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        content = f.read().strip()
    return content

def get_info():

    info = {'hostname': socket.gethostname()}

    # os:
    uname = subprocess.run(['uname', '-r'], capture_output=True, text=True)
    with open('/etc/os-release') as f:
        release = dict(line.replace('"', '').split('=') for line in f.read().splitlines() if line)
    info['os'] = {
        'release': release,
        'kernel': uname.stdout.strip()
    }
    
    # chassis:
    DMI_ROOT = '/sys/devices/virtual/dmi/id/'
    info['chassis'] = {
        'product_name': read_file(os.path.join(DMI_ROOT, 'product_name')),
        'sys_vendor': read_file(os.path.join(DMI_ROOT, 'sys_vendor')),
    }
    
    # cpu info:
    cpuinfo = {} # key->str, value->str
    lscpu = subprocess.run(['lscpu'], capture_output=True, text=True)
    for line in lscpu.stdout.splitlines():
        if not line.isspace():
            k, v = line.split(':')
            cpuinfo[k.strip()] = v.strip()
    info['cpu'] = cpuinfo

    # network (adaptor) info:
    info['net'] = {}
    NETROOT = '/sys/class/net'
    devnames = [dev for dev in os.listdir(NETROOT) if os.path.exists(os.path.join(NETROOT, dev, 'device'))]
    for dev in devnames:
        speed = read_file(os.path.join(NETROOT, dev, 'speed'))
        if not speed or int(speed) < 1:
            continue
        info['net'][dev] = {}
        info['net'][dev]['speed'] = '%s Mbits/s' % speed # Mbits/sec as per https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-class-net
        vendor_id = read_file(os.path.join(NETROOT, dev, 'device/vendor'))
        device_id = read_file(os.path.join(NETROOT, dev, 'device/device'))
        pci_id = os.path.basename(os.path.realpath(os.path.join(NETROOT, dev, 'device')))  # e.g. '0000:82:00.1'
        lspci = subprocess.run(['lspci', '-d', '%s:%s' % (vendor_id, device_id), '-nn'], capture_output=True, text=True)
        for descr in lspci.stdout.splitlines():
            if descr.split()[0] in pci_id: # descr[0] e.g. '82:00.1'
                info['net'][dev]['descr'] = descr
                break
        
        # mellanox-specific:
        mlx_port_path = [os.path.join(p) for p in glob.glob(os.path.join(NETROOT, dev, 'device', 'infiniband', 'mlx*', 'ports', '*'))]
        if mlx_port_path:
            if len(mlx_port_path) > 1:
                print('WARNING: skipping Mellanox info - cannot handle multiple ports: %r' % mlx_port, file=sys.stderr)
            mlx_port_path = mlx_port_path[0]
            info['net'][dev]['rate'] = read_file(os.path.join(mlx_port_path, 'rate')) # e.g. "100 Gb/sec (4X EDR)"
            info['net'][dev]['link_layer'] = read_file(os.path.join(mlx_port_path, 'link_layer')) # e.g. "InfiniBand"
        
    # memory info:
    # size:
    free = subprocess.run(['free', '-h', '--si'], capture_output=True, text=True)
    lines = [line.split() for line in free.stdout.splitlines()]
    if lines[0][0] != 'total' or lines[1][0] != 'Mem:':
        raise ValueError('unexpected result from free:\n%s' % free.stdout)
    meminfo = {'total': lines[1][1]}
    # types:
    mem_types = []
    for dimm in glob.glob('/sys/devices/system/edac/mc/mc*/dimm*'):
        mem_type = read_file(os.path.join(dimm, 'dimm_mem_type'))
        mem_types.append(mem_type)
    meminfo['types'] = mem_types[0] if len(set(mem_types)) == 1 else mem_types
    info['memory'] = meminfo

    return info

if __name__ == '__main__':
    if len(sys.argv) == 1:
        info = get_info()
        with open('%s.sysinfo.json' % info['hostname'], 'w') as f:
            json.dump(info, f, indent=2)
    elif len(sys.argv) > 2:
        sysname = sys.argv[1]
        infos = []
        for path in sys.argv[2:]:
            with open(path) as f:
                info = json.load(f)
                infos.append(info)
        allinfo = merge(infos)
        with open('%s.sysinfo.json' % sysname, 'w') as f:
            json.dump(allinfo, f, indent=2)
    else:
        exit('Invalid command line %r, see docstring for usage.' % ' '.join(sys.argv))
