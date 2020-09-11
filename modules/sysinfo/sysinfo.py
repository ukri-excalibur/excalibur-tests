#!/usr/bin/env python
""" Get performance-related information about host hardware.

    Usage:
        sysinfo.py
        
    Information about the current host is saved to a file `$HOSTNAME.sysinfo.json`.
    
    It requires the following shell commands to be available:
    - lscpu
    - lspci
    - free
    
    Root should not be required.
"""

import subprocess, pprint, collections, os, glob, socket, json, sys

def read_file(path, default=''):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        content = f.read().strip()
    return content

def get_info():
    """ Return a nested dict with information from the current host """

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
        
        # pause options:
        ethtool_pause = subprocess.run(['ethtool', '--show-pause', dev], capture_output=True, text=True)
        pause_info = []
        for line in ethtool_pause.stdout.splitlines()[1:]:
            if not line:
                continue
            pause_info.append('%s=%s' % tuple(v.strip() for v in line.split(':')))
        #info['net'][dev]['pause_opts'] = ','.join(pause_info)
        info['net'][dev]['pause_opts'] = pause_info

        #  RX/TX ring parameters
        ethtool_ring = subprocess.run(['ethtool', '--show-ring', dev], capture_output=True, text=True)
        ring_info_max = []
        ring_info_curr = []
        for line in ethtool_ring.stdout.splitlines()[1:]:
            if not line:
                continue
            if 'Pre-set maximums' in line:
                ring_info = ring_info_max
            elif 'Current hardware settings' in line:
                ring_info = ring_info_curr
            else:
                ring_info.append('%s=%s' % tuple(v.strip() for v in line.split(':')))
        # info['net'][dev]['ring_max'] = ','.join(ring_info_max)
        # info['net'][dev]['ring_curr'] = ','.join(ring_info_curr)
        info['net'][dev]['ring_max'] = ring_info_max
        info['net'][dev]['ring_curr'] = ring_info_curr
    
        # features:
        ethtool_features = subprocess.run(['ethtool', '--show-features', dev], capture_output=True, text=True)
        feature_info = []
        for line in ethtool_features.stdout.splitlines()[1:]:
            if not line:
                continue
            feature_info.append('%s=%s' % tuple(v.strip() for v in line.split(':')))
        # info['net'][dev]['features'] = ','.join(feature_info)
        info['net'][dev]['features'] = feature_info

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

def interrogate_host():
    """ CLI entry point for first usage in docstring. """
    info = get_info()
    with open('%s.sysinfo.json' % info['hostname'], 'w') as f:
        json.dump(info, f, indent=2)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        interrogate_host()
    else:
        exit('Invalid command line %r, see docstring for usage.' % ' '.join(sys.argv))
