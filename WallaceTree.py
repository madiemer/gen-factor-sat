import collections
import itertools

import Circuit
from Circuit import ZERO


def wallace_tree(xs, ys, circuit):
    merged = collections.defaultdict(list)

    products = weighted_product(xs, ys, circuit)
    for w, x in products:
        merged[w].append(x)

    while any(len(xs) > 2 for _, xs in merged.items()):
        tmp = collections.defaultdict(list)

        dicts = list(itertools.chain.from_iterable(map(lambda kv: add_layer(kv[0], kv[1], circuit), merged.items())))
        for w, x in dicts:
            tmp[w].append(x)

        merged = tmp

    last_carry = ZERO
    result = []
    for key in sorted(merged):
        xs = merged[key]

        if len(xs) == 1:
            x, = xs
            sum, carry = Circuit.half_adder(x, last_carry, circuit)
            last_carry = carry
            result = [sum] + result
        else:
            x, y = xs
            sum, carry = Circuit.full_adder(x, y, last_carry, circuit)
            last_carry = carry
            result = [sum] + result

    return [last_carry] + result


def weighted_product(xs, ys, circuit):
    len_xs = len(xs)
    len_ys = len(ys)

    for i, x in enumerate(xs):
        w_x = len_xs - i

        for j, y in enumerate(ys):
            w_y = len_ys - j

            weight_sum = w_x + w_y
            product = circuit.wire_and(x, y)

            yield weight_sum, product


def add_layer(w, xs, circuit):
    if len(xs) == 1:
        return [(w, xs[0])]

    elif len(xs) == 2:
        x, y = xs[:2]
        sum, carry = Circuit.half_adder(x, y, circuit)

        return [(w, sum), (w + 1, carry)]

    elif len(xs) > 2:
        x, y, z = xs[:3]
        sum, carry = Circuit.full_adder(x, y, z, circuit)
        return [(w, sum), (w + 1, carry)] + [(w, x) for x in xs[3:]]
