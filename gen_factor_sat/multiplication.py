import collections
import itertools
from typing import List, Tuple, DefaultDict, Iterable

from gen_factor_sat import circuit
from gen_factor_sat.strategies import Strategy, T


def karatsuba(xs: List[T], ys: List[T], strategy: Strategy[T], min_len=20) -> List[T]:
    n = max(len(xs), len(ys))

    if n <= min_len:
        return wallace_tree(xs, ys, strategy)
    else:
        half = (n + 1) // 2

        x1 = xs[:-half]
        x0 = xs[-half:]

        y1 = ys[:-half]
        y0 = ys[-half:]

        z0 = karatsuba(x0, y0, strategy) if x0 and y0 else []
        z2 = karatsuba(x1, y1, strategy) if x1 and y1 else []

        # z1 = karatsuba((x1 + x0), (y1 + y0)) - z2 - z0
        sum_x = circuit.n_bit_adder(x1, x0, strategy.zero(), strategy) if x1 else x0
        sum_y = circuit.n_bit_adder(y1, y0, strategy.zero(), strategy) if y1 else y0

        z1 = karatsuba(sum_x, sum_y, strategy)
        z1 = circuit.subtract(z1, z2, strategy) if z2 else z1
        z1 = circuit.subtract(z1, z0, strategy) if z0 else z1

        # x * y = z2 * 2^(2 * half) + z1 * 2^(half) + z0
        sum = circuit.n_bit_adder(circuit.shift(z2, half, strategy), z1, strategy.zero(), strategy)
        sum = circuit.n_bit_adder(circuit.shift(sum, half, strategy), z0, strategy.zero(), strategy)

        return sum


def wallace_tree(xs: List[T], ys: List[T], strategy: Strategy[T]) -> List[T]:
    products = _weighted_product(xs, ys, strategy)
    grouped_products = _group(products)

    while any(len(xs) > 2 for _, xs in grouped_products.items()):
        products = itertools.chain.from_iterable(
            [_add_layer(w, xs, strategy) for w, xs in grouped_products.items()]
        )

        grouped_products = _group(products)

    result = []
    last_carry = strategy.zero()
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


def _weighted_product(xs: List[T], ys: List[T], strategy: Strategy[T]):
    len_xs = len(xs)
    len_ys = len(ys)

    for i, x in enumerate(xs):
        w_x = len_xs - i

        for j, y in enumerate(ys):
            w_y = len_ys - j

            weight_sum = w_x + w_y
            product = strategy.wire_and(x, y)

            yield weight_sum, product


def _add_layer(w: int, xs: List[T], strategy: Strategy[T]) -> List[Tuple[int, T]]:
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


def _group(xs: Iterable[Tuple[int, T]]) -> DefaultDict[int, List[T]]:
    result = collections.defaultdict(list)
    for k, v in xs:
        result[k].append(v)

    return result
