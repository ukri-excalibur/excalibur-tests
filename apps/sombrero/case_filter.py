from enum import IntEnum
import itertools as it

class Idx(IntEnum):
    # See _flatten_nested_case() and generate()
    strong_or_weak = 0
    size = 1
    partition = 2
    nprocesses = 3
    nprocesses_per_node = 4
    theory_id = 5

def _flatten_nested_case(nested_case):
    # See Idx and generate()
    return (
        nested_case[0],  # strong/weak
        nested_case[1],  # size
        *nested_case[2],  # input from scaling config
        nested_case[3])  # theory_id

def _check_nprocesses(np):
    '''
    Make sure the number of processes is 2^n or 2^n x 3
    '''
    assert np > 0
    if np % 2 == 1:
        return np in [1, 3]
    else:
        return _check_nprocesses(np // 2)

def _case_filter(case):
    strong_or_weak = case[Idx.strong_or_weak]
    size = case[Idx.size]
    nprocesses = case[Idx.nprocesses]

    if not _check_nprocesses(nprocesses):
        return False
    if strong_or_weak == "weak" and size != "medium":
        return False

    return True

def generate(scaling_config):
    theory_ids = range(1, 7)
    sizes = ['small', 'medium', 'large', 'very_large']
    strong_or_weak = ['strong', 'weak']

    # See Idx and _flatten_nested_case()
    nested_cases = it.product(strong_or_weak, sizes, scaling_config(),
                              theory_ids)

    cases = map(_flatten_nested_case, nested_cases)

    filtered = filter(_case_filter, cases)

    filtered_list = list(filtered)
    for case in filtered_list:
        assert len(case) == 6
    return filtered_list
