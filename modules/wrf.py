""" Read a WRF output file """

import re

def extract_timings(rsl_error_path):
    step_times = []
    with open(rsl_error_path) as f:
        for line in f:
            match = re.search(r'Timing for main: time \S+ on domain\s+\d+:\s+([\d.]+) elapsed seconds', line)
            if match is not None:
                step_times.append(float(match.group(1)))
    return step_times
        
if __name__ == '__main__':
    import sys
    stats = extract_timings(sys.argv[1])
    print(stats)
