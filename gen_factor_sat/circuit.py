import functools
import itertools
from typing import List, Tuple

from gen_factor_sat.strategies import T, Strategy


def half_adder(input_1: T, input_2: T, strategy: Strategy[T]) -> Tuple[T, T]:
    output_sum = strategy.wire_or(
        strategy.wire_and(input_1, strategy.wire_not(input_2)),
        strategy.wire_and(strategy.wire_not(input_1), input_2)
    )

    output_carry = strategy.wire_and(input_1, input_2)

    return output_sum, output_carry


def full_adder(input_1: T, input_2: T, carry: T, strategy: Strategy[T]) -> Tuple[T, T]:
    partial_sum, carry_1 = half_adder(input_1, input_2, strategy)
    output_sum, carry_2 = half_adder(partial_sum, carry, strategy)

    output_carry = strategy.wire_or(carry_1, carry_2)

    return output_sum, output_carry


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


def n_bit_adder(inputs_1: List[T], inputs_2: List[T], carry: T, strategy: Strategy[T]) -> List[T]:
    if not inputs_1:
        return propagate(inputs_2, carry, strategy)
    elif not inputs_2:
        return propagate(inputs_1, carry, strategy)
    else:
        *init_1, lsb_1 = inputs_1
        *init_2, lsb_2 = inputs_2

        lsb_sum, lsb_carry = full_adder(lsb_1, lsb_2, carry, strategy)
        init_sum = n_bit_adder(init_1, init_2, lsb_carry, strategy)

        return init_sum + [lsb_sum]


def propagate(inputs: List[T], carry: T, strategy: Strategy[T]) -> List[T]:
    if not inputs:
        return [carry]
    else:
        *init, lsb = inputs

        lsb_sum, lsb_carry = half_adder(lsb, carry, strategy)
        init_sum = propagate(init, lsb_carry, strategy)

        return init_sum + [lsb_sum]


def subtract(inputs_1: List[T], inputs_2: List[T], strategy: Strategy[T]) -> List[T]:
    aligned_inputs_1, aligned_inputs_2 = align(inputs_1, inputs_2, strategy)

    complement = list(map(strategy.wire_not, aligned_inputs_2))
    output_sum = n_bit_adder(aligned_inputs_1, complement, strategy.one(), strategy)

    return output_sum[1:]  # Carry is not needed


def equality(input_1: T, input_2: T, strategy: Strategy[T]) -> T:
    return strategy.wire_or(
        strategy.wire_and(input_1, input_2),
        strategy.wire_and(
            strategy.wire_not(input_1),
            strategy.wire_not(input_2)
        )
    )


def n_bit_equality(inputs_1: List[T], inputs_2: List[T], strategy: Strategy[T]) -> T:
    aligned_inputs_1, aligned_inputs_2 = align(inputs_1, inputs_2, strategy)

    equality_circuit = functools.partial(equality, strategy=strategy)
    pairwise_equal = itertools.starmap(equality_circuit, zip(aligned_inputs_1, aligned_inputs_2))
    all_equal = functools.reduce(strategy.wire_and, pairwise_equal)

    return all_equal


def shift(inputs_1: List[T], shifts: int, strategy: Strategy[T]) -> List[T]:
    return inputs_1 + [strategy.zero()] * shifts


def align(inputs_1: List[T], inputs_2: List[T], strategy: Strategy[T]) -> Tuple[List[T], List[T]]:
    aligned_inputs_1 = ([strategy.zero()] * (len(inputs_2) - len(inputs_1))) + inputs_1
    aligned_inputs_2 = ([strategy.zero()] * (len(inputs_1) - len(inputs_2))) + inputs_2

    return aligned_inputs_1, aligned_inputs_2
