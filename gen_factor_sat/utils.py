from collections import defaultdict
from typing import Iterable, List, Tuple, DefaultDict, TypeVar


def to_bin_list(value):
    return list(to_bin_string(value))


def to_bin_string(value):
    return bin(value)[2:]


def to_int(value):
    if isinstance(value, str):
        return int(value, 2)
    elif isinstance(value, bool):
        return int(to_bin_string(value), 2)
    else:
        return int(''.join(value), 2)


K = TypeVar('K')
V = TypeVar('V')


def group(iterable: Iterable[Tuple[K, V]]) -> DefaultDict[K, List[V]]:
    result = defaultdict(list)
    for key, value in iterable:
        result[key].append(value)

    return result


def split_at(list: List[V], index: int) -> Tuple[List[V], List[V]]:
    return list[:index], list[index:]
