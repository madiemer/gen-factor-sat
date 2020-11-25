import collections
import functools
import itertools
from typing import List, Tuple, DefaultDict, Iterable

from gen_factor_sat import circuit
from gen_factor_sat.strategies import Strategy, T


def karatsuba(factor_1: List[T], factor_2: List[T], strategy: Strategy[T], min_len=20) -> List[T]:
    max_factor_length = max(len(factor_1), len(factor_2))

    if max_factor_length <= min_len:
        return wallace_tree(factor_1, factor_2, strategy)
    else:
        half_factor_length = (max_factor_length + 1) // 2

        f1_high, f1_low = split_at(factor_1, -half_factor_length)
        f2_high, f2_low = split_at(factor_2, -half_factor_length)

        result_low = karatsuba(f1_low, f2_low, strategy) if f1_low and f2_low else []
        result_high = karatsuba(f1_high, f2_high, strategy) if f1_high and f2_high else []

        # result_mid = karatsuba((f1_high + f1_low), (f2_high + f2_low)) - result_high - result_low
        factor_1_sum = circuit.n_bit_adder(f1_high, f1_low, strategy.zero(), strategy) if f1_high else f1_low
        factor_2_sum = circuit.n_bit_adder(f2_high, f2_low, strategy.zero(), strategy) if f2_high else f2_low

        result_mid = karatsuba(factor_1_sum, factor_2_sum, strategy)
        result_mid = circuit.subtract(result_mid, result_high, strategy) if result_high else result_mid
        result_mid = circuit.subtract(result_mid, result_low, strategy) if result_low else result_mid

        # result = result_high * 2^(2 * half_factor_length) + result_mid * 2^(half_factor_length) + result_low
        shifted_high = circuit.shift(result_high, half_factor_length, strategy)
        result = circuit.n_bit_adder(shifted_high, result_mid, strategy.zero(), strategy)

        shifted_high = circuit.shift(result, half_factor_length, strategy)
        result = circuit.n_bit_adder(shifted_high, result_low, strategy.zero(), strategy)

        return result


def wallace_tree(factor_1: List[T], factor_2: List[T], strategy: Strategy[T]) -> List[T]:
    add_layer_circuit = functools.partial(_add_layer, strategy=strategy)

    products = _weighted_product(factor_1, factor_2, strategy)
    grouped_products = _group(products)

    while any(len(xs) > 2 for _, xs in grouped_products.items()):
        products = itertools.chain.from_iterable(
            itertools.starmap(add_layer_circuit, grouped_products.items())
        )

        grouped_products = _group(products)

    result = []
    last_carry = strategy.zero()
    for key in sorted(grouped_products):
        products = grouped_products[key]

        if len(products) == 1:
            x, = products
            sum, carry = circuit.half_adder(x, last_carry, strategy)
            last_carry = carry
            result.append(sum)
        else:
            x, y = products
            sum, carry = circuit.full_adder(x, y, last_carry, strategy)
            last_carry = carry
            result.append(sum)

    result.append(last_carry)
    return result[::-1]


def _weighted_product(factor_1: List[T], factor_2: List[T], strategy: Strategy[T]):
    for i, x in enumerate(factor_1):
        w_x = len(factor_1) - i

        for j, y in enumerate(factor_2):
            w_y = len(factor_2) - j

            weight_sum = w_x + w_y
            product = strategy.wire_and(x, y)

            yield weight_sum, product


def _add_layer(weight: int, products: List[T], strategy: Strategy[T]) -> List[Tuple[int, T]]:
    if len(products) == 1:
        return [(weight, products[0])]

    elif len(products) == 2:
        x, y = products
        sum, carry = circuit.half_adder(x, y, strategy)

        return [(weight, sum), (weight + 1, carry)]

    elif len(products) > 2:
        x, y, z = products[:3]
        sum, carry = circuit.full_adder(x, y, z, strategy)

        return [(weight, sum), (weight + 1, carry)] + [(weight, x) for x in products[3:]]

    else:
        raise ValueError('Cannot add a layer for an empty product')


def _group(iterable: Iterable[Tuple[int, T]]) -> DefaultDict[int, List[T]]:
    result = collections.defaultdict(list)
    for key, value in iterable:
        result[key].append(value)

    return result


def split_at(list, index):
    return list[:index], list[index:]
