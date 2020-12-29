import functools
import itertools
import operator as op
from abc import ABC
from typing import List, Tuple, TypeVar

from gen_factor_sat.circuit.interface.circuit import GateStrategy, SimpleCircuitStrategy, NBitCircuitStrategy
from gen_factor_sat.formula.symbol import Constant, constant

T = TypeVar('T')
W = TypeVar('W')


class ConstantStrategy(GateStrategy[Constant, None]):
    zero: Constant = constant('0')
    one: Constant = constant('1')

    def wire_and(self, value_1: Constant, value_2: Constant, writer: None = None) -> Constant:
        return ConstantStrategy.__with_bool(op.and_, value_1, value_2)

    def wire_or(self, value_1: Constant, value_2: Constant, writer: None = None) -> Constant:
        return ConstantStrategy.__with_bool(op.or_, value_1, value_2)

    def wire_not(self, value: Constant, writer: None = None) -> Constant:
        return ConstantStrategy.__with_bool(op.not_, value)

    @staticmethod
    def __with_bool(func, *args):
        return ConstantStrategy.__to_bin(func(*iter(map(ConstantStrategy.__to_bool, args))))

    @staticmethod
    def __to_bool(value: Constant) -> bool:
        return value == '1'

    @staticmethod
    def __to_bin(value: bool) -> Constant:
        return constant(bin(value)[2:])


class GeneralSimpleCircuitStrategy(GateStrategy[T, W], SimpleCircuitStrategy[T, W], ABC):

    def half_adder(self, value_1: T, value_2: T, writer: W) -> Tuple[T, T]:
        output_sum = self.xor(value_1, value_2, writer)
        output_carry = self.wire_and(value_1, value_2, writer)

        return output_sum, output_carry

    def full_adder(self, value_1: T, value_2: T, carry: T, writer: W) -> Tuple[T, T]:
        partial_sum, carry_1 = self.half_adder(value_1, value_2, writer)
        output_sum, carry_2 = self.half_adder(partial_sum, carry, writer)

        output_carry = self.wire_or(carry_1, carry_2, writer)

        return output_sum, output_carry

    def equality(self, value_1: T, value_2: T, writer: W) -> T:
        return self.wire_or(
            self.wire_and(
                value_1,
                value_2,
                writer
            ),
            self.wire_and(
                self.wire_not(value_1, writer),
                self.wire_not(value_2, writer),
                writer
            ),
            writer
        )

    def xor(self, value_1: T, value_2: T, writer: W) -> T:
        return self.wire_or(
            self.wire_and(
                value_1,
                self.wire_not(value_2, writer),
                writer
            ),
            self.wire_and(
                self.wire_not(value_1, writer),
                value_2,
                writer
            ),
            writer
        )


class GeneralNBitCircuitStrategy(GateStrategy[T, W], SimpleCircuitStrategy[T, W], NBitCircuitStrategy[T, W],
                                 ABC):

    def n_bit_adder(self, number_1: List[T], number_2: List[T], carry: T, writer: W) -> List[T]:
        if not number_1:
            return self.propagate(number_2, carry, writer)
        elif not number_2:
            return self.propagate(number_1, carry, writer)
        else:
            *init_1, lsb_1 = number_1
            *init_2, lsb_2 = number_2

            lsb_sum, lsb_carry = self.full_adder(lsb_1, lsb_2, carry, writer)
            init_sum = self.n_bit_adder(init_1, init_2, lsb_carry, writer)

            return init_sum + [lsb_sum]

    def propagate(self, inputs: List[T], carry: T, writer: W) -> List[T]:
        if not inputs:
            return [carry]
        else:
            *init, lsb = inputs

            lsb_sum, lsb_carry = self.half_adder(lsb, carry, writer)
            init_sum = self.propagate(init, lsb_carry, writer)

            return init_sum + [lsb_sum]

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

    def subtract(self, number_1: List[T], number_2: List[T], writer: W) -> List[T]:
        if self.all_zero(number_2):
            return number_1
        else:
            aligned_number_1, aligned_number_2 = self.align(number_1, number_2, writer)

            complement = list(map(functools.partial(self.wire_not, writer=writer), aligned_number_2))
            output_sum = self.n_bit_adder(aligned_number_1, complement, self.one, writer)

            return output_sum[1:]  # Carry is not needed

    def n_bit_equality(self, number_1: List[T], number_2: List[T], writer: W) -> T:
        aligned_number_1, aligned_number_2 = self.align(number_1, number_2, writer)

        pairwise_equal = itertools.starmap(functools.partial(self.equality, writer=writer),
                                           zip(aligned_number_1, aligned_number_2))

        all_equal = functools.reduce(functools.partial(self.wire_and, writer=writer), pairwise_equal)

        return all_equal

    def shift(self, number: List[T], shifts: int, writer: W) -> List[T]:
        return number + [self.zero] * shifts

    def align(self, number_1: List[T], number_2: List[T], writer: W) -> Tuple[List[T], List[T]]:
        aligned_number_1 = ([self.zero] * (len(number_2) - len(number_1))) + number_1
        aligned_number_2 = ([self.zero] * (len(number_1) - len(number_2))) + number_2

        return aligned_number_1, aligned_number_2

    def all_zero(self, number: List[T]):
        return all(self.is_zero(value) for value in number)

    def normalize(self, number: List[T]) -> List[T]:
        return list(itertools.dropwhile(self.is_zero, number))
