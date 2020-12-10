import functools
import itertools
import operator as op
from abc import ABC, abstractmethod
from typing import Sequence, List, MutableSequence
from typing import Tuple, Generic, TypeVar

from gen_factor_sat.tseitin_encoding import Constant, constant

T = TypeVar('T')
W = TypeVar('W')


class GateStrategy(Generic[T, W], ABC):

    @property
    @abstractmethod
    def zero(self) -> T:
        pass

    @property
    @abstractmethod
    def one(self) -> T:
        pass

    @abstractmethod
    def wire_and(self, x: T, y: T, writer: W = None) -> T:
        pass

    @abstractmethod
    def wire_or(self, x: T, y: T, writer: W = None) -> T:
        pass

    @abstractmethod
    def wire_not(self, x: T, writer: W = None) -> T:
        pass

    def is_constant(self, x: T) -> bool:
        return (x == self.zero) or (x == self.one)


class ConstantStrategy(GateStrategy[Constant, None]):
    zero: Constant = constant('0')
    one: Constant = constant('1')

    def wire_and(self, x: Constant, y: Constant, writer: None = None) -> Constant:
        return ConstantStrategy.__with_bool(op.and_, x, y)

    def wire_or(self, x: Constant, y: Constant, writer: None = None) -> Constant:
        return ConstantStrategy.__with_bool(op.or_, x, y)

    def wire_not(self, x: Constant, writer: None = None) -> Constant:
        return ConstantStrategy.__with_bool(op.not_, x)

    @staticmethod
    def __with_bool(func, *args):
        return ConstantStrategy.__to_bin(func(*iter(map(ConstantStrategy.__to_bool, args))))

    @staticmethod
    def __to_bool(value: Constant) -> bool:
        return value == '1'

    @staticmethod
    def __to_bin(value: bool) -> Constant:
        return constant(bin(value)[2:])


class SimpleCircuitStrategy(Generic[T, W], ABC):

    @abstractmethod
    def half_adder(self, input_1: T, input_2: T, writer: W = None) -> Tuple[T, T]:
        pass

    @abstractmethod
    def full_adder(self, input_1: T, input_2: T, carry: T, writer: W = None) -> Tuple[T, T]:
        pass

    @abstractmethod
    def equality(self, input_1: T, input_2: T, writer: W = None) -> T:
        pass

    @abstractmethod
    def xor(self, input_1: T, input_2: T, writer: W = None) -> T:
        pass


class GeneralSimpleCircuitStrategy(GateStrategy[T, W], SimpleCircuitStrategy[T, W], ABC):

    def half_adder(self, input_1: T, input_2: T, writer: W = None) -> Tuple[T, T]:
        output_sum = self.xor(input_1, input_2, writer)
        output_carry = self.wire_and(input_1, input_2, writer)

        return output_sum, output_carry

    def full_adder(self, input_1: T, input_2: T, carry: T, writer: W = None) -> Tuple[T, T]:
        partial_sum, carry_1 = self.half_adder(input_1, input_2, writer)
        output_sum, carry_2 = self.half_adder(partial_sum, carry, writer)

        output_carry = self.wire_or(carry_1, carry_2, writer)

        return output_sum, output_carry

    def equality(self, input_1: T, input_2: T, writer: W = None) -> T:
        return self.wire_or(
            self.wire_and(
                input_1,
                input_2,
                writer
            ),
            self.wire_and(
                self.wire_not(input_1, writer),
                self.wire_not(input_2, writer),
                writer
            ),
            writer
        )

    def xor(self, input_1: T, input_2: T, writer: W = None) -> T:
        return self.wire_or(
            self.wire_and(
                input_1,
                self.wire_not(input_2, writer),
                writer
            ),
            self.wire_and(
                self.wire_not(input_1, writer),
                input_2,
                writer
            ),
            writer
        )


class NBitCircuitStrategy(Generic[T, W], ABC):

    @abstractmethod
    def n_bit_adder(self, inputs_1: Sequence[T], inputs_2: Sequence[T], carry: T, writer: W = None) -> Sequence[T]:
        pass

    @abstractmethod
    def subtract(self, inputs_1: Sequence[T], inputs_2: Sequence[T], writer: W = None) -> Sequence[T]:
        pass

    @abstractmethod
    def n_bit_equality(self, inputs_1: Sequence[T], inputs_2: Sequence[T], writer: W = None) -> T:
        pass

    @abstractmethod
    def shift(self, inputs_1: Sequence[T], shifts: int, writer: W = None) -> Sequence[T]:
        pass

    @abstractmethod
    def align(self, inputs_1: Sequence[T], inputs_2: Sequence[T], writer: W = None) -> Tuple[Sequence[T], Sequence[T]]:
        pass


class GeneralNBitCircuitStrategy(GateStrategy[T, W], SimpleCircuitStrategy[T, W], NBitCircuitStrategy[T, W], ABC):

    def n_bit_adder(self, inputs_1: Sequence[T], inputs_2: Sequence[T], carry: T, writer: W = None) -> Sequence[T]:
        if not inputs_1:
            return self.propagate(inputs_2, carry, writer)
        elif not inputs_2:
            return self.propagate(inputs_1, carry, writer)
        else:
            *init_1, lsb_1 = inputs_1
            *init_2, lsb_2 = inputs_2

            lsb_sum, lsb_carry = self.full_adder(lsb_1, lsb_2, carry, writer)
            init_sum = self.n_bit_adder(init_1, init_2, lsb_carry, writer)

            return init_sum + [lsb_sum]

    def propagate(self, inputs: Sequence[T], carry: T, writer: W = None) -> Sequence[T]:
        if not inputs:
            return [carry]
        else:
            *init, lsb = inputs

            lsb_sum, lsb_carry = self.half_adder(lsb, carry, writer)
            init_sum = self.propagate(init, lsb_carry, writer)

            return init_sum + [lsb_sum]

    # def n_bit_adder(xs: Sequence[T], ys: Sequence[T], c: T, strategy: Strategy[T]) -> Sequence[T]:
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

    def subtract(self, inputs_1: Sequence[T], inputs_2: Sequence[T], writer: W = None) -> Sequence[T]:
        aligned_inputs_1, aligned_inputs_2 = self.align(inputs_1, inputs_2, writer)

        complement = list(map(functools.partial(self.wire_not, writer=writer), aligned_inputs_2))
        output_sum = self.n_bit_adder(aligned_inputs_1, complement, self.one, writer)

        return output_sum[1:]  # Carry is not needed

    def n_bit_equality(self, inputs_1: Sequence[T], inputs_2: Sequence[T], writer: W = None) -> T:
        aligned_inputs_1, aligned_inputs_2 = self.align(inputs_1, inputs_2, writer)

        pairwise_equal = itertools.starmap(functools.partial(self.equality, writer=writer),
                                           zip(aligned_inputs_1, aligned_inputs_2))

        all_equal = functools.reduce(functools.partial(self.wire_and, writer=writer), pairwise_equal)

        return all_equal

    def shift(self, inputs_1: Sequence[T], shifts: int, writer: W = None) -> Sequence[T]:
        return inputs_1 + [self.zero] * shifts

    def align(self, inputs_1: Sequence[T], inputs_2: Sequence[T], writer: W = None) -> Tuple[List[T], List[T]]:
        aligned_inputs_1 = ([self.zero] * (len(inputs_2) - len(inputs_1))) + inputs_1
        aligned_inputs_2 = ([self.zero] * (len(inputs_1) - len(inputs_2))) + inputs_2

        return aligned_inputs_1, aligned_inputs_2
