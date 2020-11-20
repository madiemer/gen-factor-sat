import functools
from typing import List, Tuple

from gen_factor_sat.strategies import T, Strategy, ZERO, ONE


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


# def n_bit_adder(xs: List[T], ys: List[T], c: T, strategy: Strategy[T]) -> List[T]:
#     aligned_xs, aligned_ys = align(xs, ys)
#
#     carry = c
#     result = []
#     for i in range(len(aligned_xs)):
#         x = aligned_xs[-(i+1)]
#         y = aligned_ys[-(i+1)]
#
#         sum_xy, carry_xy = full_adder(x, y, carry, strategy)
#
#         carry = carry_xy
#         result.append(sum_xy)
#
#     result.append(carry)
#     result.reverse()
#     return result


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
    aligned_xs, aligned_ys = align(xs, ys)
    complement = list(map(strategy.wire_not, aligned_ys))
    sum = n_bit_adder(aligned_xs, complement, ONE, strategy)

    return sum[1:]  # Carry is not needed


def equality(x: T, y: T, strategy: Strategy[T]) -> T:
    return strategy.wire_or(
        strategy.wire_and(x, y),
        strategy.wire_and(
            strategy.wire_not(x),
            strategy.wire_not(y)
        )
    )


def n_bit_equality(xs: List[T], ys: List[T], strategy: Strategy[T]) -> T:
    aligned_xs, aligned_ys = align(xs, ys)

    pairwise_equal = [equality(x, y, strategy) for x, y in zip(aligned_xs, aligned_ys)]
    all_equal = functools.reduce(strategy.wire_and, pairwise_equal)

    return all_equal


def shift(xs: List[T], n: int) -> List[T]:
    return xs + [ZERO] * n


def align(xs: List[T], ys: List[T]) -> Tuple[List[T], List[T]]:
    aligned_xs = ([ZERO] * (len(ys) - len(xs))) + xs
    aligned_ys = ([ZERO] * (len(xs) - len(ys))) + ys

    return aligned_xs, aligned_ys
