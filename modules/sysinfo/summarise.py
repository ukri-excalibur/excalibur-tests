""" Combine all  `*.sysinfo.json` files in the working directory into a single `sysinfo.json` file.

"""

import glob, pprint, json

# can't use modules.utils.diff_dicts as the dicts there must not contain dicts themselves :-(

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
        #print('vals:', vals)
        if len(vals) != (len(dicts)):
            raise ValueError('At least one dict is missing key at %s' % '.'.join(path + [str(key)]))
        elif len(set(type(v) for v in vals)) > 1:
            raise ValueError('More than one type of value for key at %s' % '.'.join(path + [str(key)]))
        elif isinstance(vals[0], dict):
            result[key] = merge(vals, path + [str(key)])
        elif isinstance(vals[0], list):
            vals = [tuple(v) for v in vals]
        else:
            try:
                unique_vals = set(vals)
            except Exception:
                raise
            if len(unique_vals) == 1:
                result[key] = vals[0]
            else:
                result[key] = vals
    return result

if __name__ == '__main__':
    infos = []
    for path in glob.glob('*.sysinfo.json'):
        with open(path) as f:
            info = json.load(f)
            infos.append(info)
    q = merge(infos)
    with open('sysinfo.json', 'w') as f:
        json.dump(q, f)
