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
