import functools
import itertools
import operator as op
from abc import ABC, abstractmethod
from typing import List
from typing import Tuple, Generic, TypeVar

from gen_factor_sat.tseitin_encoding import Constant, constant

T = TypeVar('T')


class GateStrategy(Generic[T], ABC):

    @property
    @abstractmethod
    def zero(self) -> T:
        pass

    @property
    @abstractmethod
    def one(self) -> T:
        pass

    @abstractmethod
    def wire_and(self, x: T, y: T) -> T:
        pass

    @abstractmethod
    def wire_or(self, x: T, y: T) -> T:
        pass

    @abstractmethod
    def wire_not(self, x: T) -> T:
        pass

    def is_constant(self, x: T) -> bool:
        return (x == self.zero) or (x == self.one)


class ConstantStrategy(GateStrategy[Constant]):
    zero: Constant = constant('0')
    one: Constant = constant('1')

    def wire_and(self, x: Constant, y: Constant) -> Constant:
        return ConstantStrategy.__with_bool(op.and_, x, y)

    def wire_or(self, x: Constant, y: Constant) -> Constant:
        return ConstantStrategy.__with_bool(op.or_, x, y)

    def wire_not(self, x: Constant) -> Constant:
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


class CircuitStrategy(Generic[T], ABC):

    @abstractmethod
    def half_adder(self, input_1: T, input_2: T) -> Tuple[T, T]:
        pass

    @abstractmethod
    def full_adder(self, input_1: T, input_2: T, carry: T) -> Tuple[T, T]:
        pass

    @abstractmethod
    def equality(self, input_1: T, input_2: T) -> T:
        pass

    @abstractmethod
    def xor(self, input_1: T, input_2: T) -> T:
        pass


class GeneralCircuitStrategy(CircuitStrategy[T]):

    def __init__(self, gate_strategy: GateStrategy[T]):
        self.gate_strategy = gate_strategy

    def half_adder(self, input_1: T, input_2: T) -> Tuple[T, T]:
        output_sum = self.xor(input_1, input_2)
        output_carry = self.gate_strategy.wire_and(input_1, input_2)

        return output_sum, output_carry

    def full_adder(self, input_1: T, input_2: T, carry: T) -> Tuple[T, T]:
        partial_sum, carry_1 = self.half_adder(input_1, input_2)
        output_sum, carry_2 = self.half_adder(partial_sum, carry)

        output_carry = self.gate_strategy.wire_or(carry_1, carry_2)

        return output_sum, output_carry

    def equality(self, input_1: T, input_2: T) -> T:
        return self.gate_strategy.wire_or(
            self.gate_strategy.wire_and(input_1, input_2),
            self.gate_strategy.wire_and(
                self.gate_strategy.wire_not(input_1),
                self.gate_strategy.wire_not(input_2)
            )
        )

    def xor(self, input_1: T, input_2: T) -> T:
        return self.gate_strategy.wire_or(
            self.gate_strategy.wire_and(input_1, self.gate_strategy.wire_not(input_2)),
            self.gate_strategy.wire_and(self.gate_strategy.wire_not(input_1), input_2)
        )


class NBitCircuitStrategy(Generic[T], ABC):

    @abstractmethod
    def n_bit_adder(self, inputs_1: List[T], inputs_2: List[T], carry: T) -> List[T]:
        pass

    @abstractmethod
    def subtract(self, inputs_1: List[T], inputs_2: List[T]) -> List[T]:
        pass

    @abstractmethod
    def n_bit_equality(self, inputs_1: List[T], inputs_2: List[T]) -> T:
        pass

    @abstractmethod
    def shift(self, inputs_1: List[T], shifts: int) -> List[T]:
        pass

    @abstractmethod
    def align(self, inputs_1: List[T], inputs_2: List[T]) -> Tuple[List[T], List[T]]:
        pass


class GeneralNBitCircuitStrategy(NBitCircuitStrategy[T]):

    def __init__(self, gate_strategy: GateStrategy[T], circuit_strategy: GeneralCircuitStrategy[T]):
        self.gate_strategy = gate_strategy
        self.circuit_strategy = circuit_strategy

    def n_bit_adder(self, inputs_1: List[T], inputs_2: List[T], carry: T) -> List[T]:
        if not inputs_1:
            return self.propagate(inputs_2, carry)
        elif not inputs_2:
            return self.propagate(inputs_1, carry)
        else:
            *init_1, lsb_1 = inputs_1
            *init_2, lsb_2 = inputs_2

            lsb_sum, lsb_carry = self.circuit_strategy.full_adder(lsb_1, lsb_2, carry)
            init_sum = self.n_bit_adder(init_1, init_2, lsb_carry)

            return init_sum + [lsb_sum]

    def propagate(self, inputs: List[T], carry: T) -> List[T]:
        if not inputs:
            return [carry]
        else:
            *init, lsb = inputs

            lsb_sum, lsb_carry = self.circuit_strategy.half_adder(lsb, carry)
            init_sum = self.propagate(init, lsb_carry)

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

    def subtract(self, inputs_1: List[T], inputs_2: List[T]) -> List[T]:
        aligned_inputs_1, aligned_inputs_2 = self.align(inputs_1, inputs_2)

        complement = list(map(self.gate_strategy.wire_not, aligned_inputs_2))
        output_sum = self.n_bit_adder(aligned_inputs_1, complement, self.gate_strategy.one)

        return output_sum[1:]  # Carry is not needed

    def n_bit_equality(self, inputs_1: List[T], inputs_2: List[T]) -> T:
        aligned_inputs_1, aligned_inputs_2 = self.align(inputs_1, inputs_2)

        pairwise_equal = itertools.starmap(self.circuit_strategy.equality, zip(aligned_inputs_1, aligned_inputs_2))
        all_equal = functools.reduce(self.gate_strategy.wire_and, pairwise_equal)

        return all_equal

    def shift(self, inputs_1: List[T], shifts: int) -> List[T]:
        return inputs_1 + [self.gate_strategy.zero] * shifts

    def align(self, inputs_1: List[T], inputs_2: List[T]) -> Tuple[List[T], List[T]]:
        aligned_inputs_1 = ([self.gate_strategy.zero] * (len(inputs_2) - len(inputs_1))) + inputs_1
        aligned_inputs_2 = ([self.gate_strategy.zero] * (len(inputs_1) - len(inputs_2))) + inputs_2

        return aligned_inputs_1, aligned_inputs_2
