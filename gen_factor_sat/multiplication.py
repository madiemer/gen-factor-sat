import collections
import itertools
from typing import List, Tuple, DefaultDict, Iterable

from gen_factor_sat import circuit
from gen_factor_sat.circuit import ZERO
from gen_factor_sat.strategy import Strategy, T


def karatsuba(xs: List[T], ys: List[T], strategy: Strategy[T]) -> List[T]:
    if len(xs) < 20 or len(ys) < 20:
        return wallace_tree(xs, ys, strategy)

    n = max(len(xs), len(ys))
    half = (n + 1) // 2

    x1 = xs[:-half]
    x0 = xs[-half:]

    y1 = ys[:-half]
    y0 = ys[-half:]

    z0 = karatsuba(x0, y0, strategy)
    z2 = karatsuba(x1, y1, strategy) if x1 and y1 else ['0']

    # z1 = karatsuba((x1 + x0), (y1 + y0)) - z2 - z0
    sum_x = circuit.n_bit_adder(x1, x0, ZERO, strategy) if x1 else x0
    sum_y = circuit.n_bit_adder(y1, y0, ZERO, strategy) if y1 else y0

    z1 = karatsuba(sum_x, sum_y, strategy)
    z1 = circuit.subtract(z1, z2, strategy)
    z1 = circuit.subtract(z1, z0, strategy)

    # x * y = z2 * 2^(2 * half) + z1 * 2^(half) + z0
    sum = circuit.n_bit_adder(circuit.shift(z2, half), z1, ZERO, strategy)
    sum = circuit.n_bit_adder(circuit.shift(sum, half), z0, ZERO, strategy)

    return sum


def wallace_tree(xs: List[T], ys: List[T], strategy: Strategy[T]) -> List[T]:
    products = weighted_product(xs, ys, strategy)
    grouped_products = group(products)

    while any(len(xs) > 2 for _, xs in grouped_products.items()):
        products = itertools.chain.from_iterable(
            [add_layer(w, xs, strategy) for w, xs in grouped_products.items()]
        )

        grouped_products = group(products)

    result = []
    last_carry = ZERO
    for key in sorted(grouped_products):
        xs = grouped_products[key]

        if len(xs) == 1:
            x, = xs
            sum, carry = circuit.half_adder(x, last_carry, strategy)
            last_carry = carry
            result.append(sum)
        else:
            x, y = xs
            sum, carry = circuit.full_adder(x, y, last_carry, strategy)
            last_carry = carry
            result.append(sum)

    result.append(last_carry)
    return result[::-1]


def weighted_product(xs: List[T], ys: List[T], strategy: Strategy[T]):
    len_xs = len(xs)
    len_ys = len(ys)

    for i, x in enumerate(xs):
        w_x = len_xs - i

        for j, y in enumerate(ys):
            w_y = len_ys - j

            weight_sum = w_x + w_y
            product = strategy.wire_and(x, y)

            yield weight_sum, product


def add_layer(w: int, xs: List[T], strategy: Strategy[T]) -> List[Tuple[int, T]]:
    if len(xs) == 1:
        return [(w, xs[0])]

    elif len(xs) == 2:
        x, y = xs
        sum, carry = circuit.half_adder(x, y, strategy)

        return [(w, sum), (w + 1, carry)]

    elif len(xs) > 2:
        x, y, z = xs[:3]
        sum, carry = circuit.full_adder(x, y, z, strategy)

        return [(w, sum), (w + 1, carry)] + [(w, x) for x in xs[3:]]


def group(xs: Iterable[Tuple[int, T]]) -> DefaultDict[int, List[T]]:
    result = collections.defaultdict(list)
    for k, v in xs:
        result[k].append(v)

    return result
