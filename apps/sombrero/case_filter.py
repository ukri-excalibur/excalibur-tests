from enum import IntEnum
import itertools as it


class Idx(IntEnum):
    # See _flatten_nested_case() and generate()
    strong_or_weak = 0
    size = strong_or_weak + 1
    partition = size + 1
    nprocesses = partition + 1
    nprocesses_per_node = nprocesses + 1
    idx_max = nprocesses_per_node + 1


def _flatten_nested_case(nested_case):
    # See Idx and generate()
    res = [None] * Idx.idx_max

    (
        res[Idx.strong_or_weak],  #
        res[Idx.size],  #
        (
            res[Idx.partition],  #
            res[Idx.nprocesses],  #
            res[Idx.nprocesses_per_node])) = nested_case

    return tuple(res)


def _check_nprocesses(np):
    '''
    Make sure the number of processes is 2^n or 2^n x 3
    '''
    assert np > 0
    if np % 2 == 1:
        return np in [1, 3]
    else:
        return _check_nprocesses(np // 2)


global_sizes = {
    'small': 24**3 * 32,
    'medium': 48**3 * 64,
    'large': 64**3 * 96,
    'very_large': 96**3 * 128,
}


def _case_filter(case):
    strong_or_weak = case[Idx.strong_or_weak]
    size = case[Idx.size]
    nprocesses = case[Idx.nprocesses]

    if not _check_nprocesses(nprocesses):
        return False
    if strong_or_weak == "weak" and size != "medium":
        return False

    min_size = 4**4  # Sombrero would not accept these anyway
    max_size = 24**3 * 32  # the size of the smallest global lattice

    local_size = global_sizes[size] / nprocesses

    if not min_size <= local_size <= max_size:
        return False

    return True


def generate(scaling_config):
    strong_or_weak = ['strong', 'weak']

    # See Idx and _flatten_nested_case()
    nested_cases = it.product(strong_or_weak,
                              global_sizes.keys(),
                              scaling_config())

    cases = map(_flatten_nested_case, nested_cases)

    filtered = filter(_case_filter, cases)

    filtered_list = list(filtered)
    for case in filtered_list:
        assert len(case) == Idx.idx_max
    return filtered_list
