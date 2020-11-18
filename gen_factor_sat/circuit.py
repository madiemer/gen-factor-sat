from typing import List, Tuple

from gen_factor_sat.strategy import Strategy, T

Constant = str

ZERO = '0'
ONE = '1'


def half_adder(x: T, y: T, strategy: Strategy[T]) -> Tuple[T, T]:
    sum = strategy.wire_or(
        strategy.wire_and(x, strategy.wire_not(y)),
        strategy.wire_and(strategy.wire_not(x), y)
    )

    carry = strategy.wire_and(x, y)

    return sum, carry


def full_adder(x: T, y: T, c: T, strategy: Strategy[T]) -> Tuple[T, T]:
    partial_sum, carry_1 = half_adder(x, y, strategy)
    total_sum, carry_2 = half_adder(partial_sum, c, strategy)

    carry = strategy.wire_or(carry_1, carry_2)

    return total_sum, carry


def n_bit_adder(xs: List[T], ys: List[T], c: T, strategy: Strategy[T]) -> List[T]:
    if not xs:
        return propagate(ys, c, strategy)
    elif not ys:
        return propagate(xs, c, strategy)
    else:
        x = xs[-1]
        y = ys[-1]
        sum_xy, carry_xy = full_adder(x, y, c, strategy)

        sum = n_bit_adder(xs[:-1], ys[:-1], carry_xy, strategy)
        return sum + [sum_xy]


def propagate(xs: List[T], c: T, strategy: Strategy[T]) -> List[T]:
    if not xs:
        return [c]
    else:
        x = xs[-1]
        partial_sum, carry = half_adder(x, c, strategy)
        total_sum = propagate(xs[:-1], carry, strategy)

        return total_sum + [partial_sum]


def subtract(xs: List[T], ys: List[T], strategy: Strategy[T]) -> List[T]:
    aligned = ([ZERO] * (len(xs) - len(ys))) + ys
    complement = list(map(strategy.wire_not, aligned))

    sum = n_bit_adder(xs, complement, ONE, strategy)
    return sum[1:]  # Carry is not needed


def shift(xs: List[T], n: int) -> List[T]:
    return xs + [ZERO] * n