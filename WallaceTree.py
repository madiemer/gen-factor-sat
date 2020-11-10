import collections
import itertools

import Circuit


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

    last_carry = 0
    result = ''
    for key in sorted(merged):
        xs = merged[key]

        if len(xs) == 1:
            x, = xs
            sum, carry = half_adder(x, last_carry, circuit)
            last_carry = carry
            result = sum + result
        else:
            x, y = xs
            sum, carry = full_adder(x, y, last_carry, circuit)
            last_carry = carry
            result = sum + result

    return (last_carry + result)


def weighted_product(xs, ys, circuit):
    len_xs = len(xs)
    len_ys = len(ys)

    for i, x in enumerate(xs):
        w_x = len_xs - i

        for j, y in enumerate(ys):
            w_y = len_ys - j

            yield (w_x + w_y, circuit.mult(x, y))

def add_layer(w, xs, circuit):
    if len(xs) == 1:
        return [(w, xs[0])]

    elif len(xs) == 2:
        x, y = xs[:2]
        s, c = half_adder(x, y, circuit)

        return [(w, s), (w + 1, c)]

    elif len(xs) > 2:
        x, y, z = xs[:3]
        s, c = full_adder(x, y, z, circuit)
        return [(w, s), (w + 1, c)] + [(w, x) for x in xs[3:]]

def half_adder(x, y, circuit):
    x_bool = x == '1'
    y_bool = y == '1'

    sum = (x_bool and (not y_bool)) or ((not x_bool) and y_bool)
    carry = x_bool and y_bool

    return bin(sum)[2:], bin(carry)[2:]

def full_adder(x, y, c, circuit):
    sum_xy, carry_1 = half_adder(x, y, circuit)
    sum_xyc, carry_2 = half_adder(sum_xy, c, circuit)

    carry = (carry_1 == '1') or (carry_2 == '1')
    return sum_xyc, bin(carry)[2:]

def n_bit_adder(xs, ys, c, circuit):
    if not xs:
        return propagate(ys, c, circuit)
    elif not ys:
        return propagate(xs, c, circuit)
    else:
        x = xs[-1]
        y = ys[-1]
        sum_xy, carry_xy = full_adder(x, y, c)

        sum, carry = n_bit_adder(xs[:-1], ys[:-1], carry_xy, circuit)
        return (sum + sum_xy), carry

def propagate(xs, c, circuit):
    return circuit.add(xs, c)