""" Get performance-related information about host hardware.

    It requires the following shell commands to be available:
    - lscpu
    - lspci
    - free
    
    Root should not be required.

    TODO: Creates a file `$HOSTNAME.sysinfo.json`.
"""

import subprocess, pprint, collections, os, glob, socket, json

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
    chassis_info = {
        'product_name': open(os.path.join(DMI_ROOT, 'product_name')).read().strip(),
        'sys_vendor': open(os.path.join(DMI_ROOT, 'sys_vendor')).read().strip(),
    }
    info['chassis'] = chassis_info

    # cpu info:
    cpuinfo = {} # key->str, value->str
    lscpu = subprocess.run(['lscpu'], capture_output=True, text=True)
    for line in lscpu.stdout.splitlines():
        if not line.isspace():
            k, v = line.split(':')
            cpuinfo[k.strip()] = v.strip()
    info['cpu'] = cpuinfo

    # network (adaptor) info:
    NETROOT = '/sys/class/net'
    devnames = [dev for dev in os.listdir(NETROOT) if os.path.exists(os.path.join(NETROOT, dev, 'device'))]
    netinfo = {}
    for dev in devnames:
        speed = open(os.path.join(NETROOT, dev, 'speed')).read().strip()
        if not speed or int(speed) < 1:
            continue
        netinfo[dev] = {'speed': '%s Mbits/s' % speed } # Mbits/sec as per https://www.kernel.org/doc/Documentation/ABI/testing/sysfs-class-net
        vendor_id = open(os.path.join(NETROOT, dev, 'device/vendor')).read().strip()
        device_id = open(os.path.join(NETROOT, dev, 'device/device')).read().strip()
        pci_id = os.path.basename(os.path.realpath(os.path.join(NETROOT, dev, 'device')))  # e.g. '0000:82:00.1'
        lspci = subprocess.run(['lspci', '-d', '%s:%s' % (vendor_id, device_id), '-nn'], capture_output=True, text=True)
        for descr in lspci.stdout.splitlines():
            if descr.split()[0] in pci_id: # descr[0] e.g. '82:00.1'
                netinfo[dev]['descr'] = descr
                break
        
        # mellanox-specific:
        mlx_port_path = [os.path.join(p) for p in glob.glob(os.path.join(NETROOT, dev, 'device', 'infiniband', 'mlx*', 'ports', '*'))]
        if mlx_port_path:
            if len(mlx_port_path) > 1:
                print('WARNING: skipping Mellanox info - cannot handle multiple ports: %r' % mlx_port)
            mlx_port_path = mlx_port_path[0]
            netinfo[dev]['rate'] = read_file(os.path.join(mlx_port_path, 'rate')) # e.g. "100 Gb/sec (4X EDR)"
            netinfo[dev]['link_layer'] = read_file(os.path.join(mlx_port_path, 'link_layer')) # e.g. "InfiniBand"

    info['net'] = netinfo
        
    # memory info:
    # size:
    free = subprocess.run(['free', '-h', '--si'], capture_output=True, text=True)
    lines = [line.split() for line in free.stdout.splitlines()]
    if lines[0][0] != 'total' or lines[1][0] != 'Mem:':
        raise ValueError('unexpected result from free:\n%s' % free.stdout)
    meminfo = {'total': lines[1][1]}
    mem_types = []
    for dimm in glob.glob('/sys/devices/system/edac/mc/mc*/dimm*'):
        mem_type = open(os.path.join(dimm, 'dimm_mem_type')).read().strip()
        mem_types.append(mem_type)
    meminfo['types'] = mem_types[0] if len(set(mem_types)) == 1 else mem_types
    info['memory'] = meminfo

    return info

if __name__ == '__main__':
    info = get_info()
    with open('%s.sysinfo.json' % info['hostname'], 'w') as f:
        json.dump(info, f, indent=2)
