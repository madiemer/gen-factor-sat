import functools
import itertools
from typing import List, Tuple, Generic, TypeVar

T = TypeVar('T')


class Circuit(Generic[T]):

    def zero(self) -> T:
        pass

    def one(self) -> T:
        pass

    def wire_and(self, x: T, y: T) -> T:
        pass

    def wire_or(self, x: T, y: T) -> T:
        pass

    def wire_not(self, x: T) -> T:
        pass

    def half_adder(self, input_1: T, input_2: T) -> Tuple[T, T]:
        output_sum = self.xor(input_1, input_2)
        output_carry = self.wire_and(input_1, input_2)

        return output_sum, output_carry

    def full_adder(self, input_1: T, input_2: T, carry: T) -> Tuple[T, T]:
        partial_sum, carry_1 = self.half_adder(input_1, input_2)
        output_sum, carry_2 = self.half_adder(partial_sum, carry)

        output_carry = self.wire_or(carry_1, carry_2)

        return output_sum, output_carry

    def equality(self, input_1: T, input_2: T) -> T:
        return self.wire_or(
            self.wire_and(input_1, input_2),
            self.wire_and(
                self.wire_not(input_1),
                self.wire_not(input_2)
            )
        )

    def xor(self, input_1: T, input_2: T) -> T:
        return self.wire_or(
            self.wire_and(input_1, self.wire_not(input_2)),
            self.wire_and(self.wire_not(input_1), input_2)
        )

    def n_bit_adder(self, inputs_1: List[T], inputs_2: List[T], carry: T) -> List[T]:
        if not inputs_1:
            return self.propagate(inputs_2, carry)
        elif not inputs_2:
            return self.propagate(inputs_1, carry)
        else:
            *init_1, lsb_1 = inputs_1
            *init_2, lsb_2 = inputs_2

            lsb_sum, lsb_carry = self.full_adder(lsb_1, lsb_2, carry)
            init_sum = self.n_bit_adder(init_1, init_2, lsb_carry)

            return init_sum + [lsb_sum]

    def propagate(self, inputs: List[T], carry: T) -> List[T]:
        if not inputs:
            return [carry]
        else:
            *init, lsb = inputs

            lsb_sum, lsb_carry = self.half_adder(lsb, carry)
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

        complement = list(map(self.wire_not, aligned_inputs_2))
        output_sum = self.n_bit_adder(aligned_inputs_1, complement, self.one())

        return output_sum[1:]  # Carry is not needed

    def n_bit_equality(self, inputs_1: List[T], inputs_2: List[T]) -> T:
        aligned_inputs_1, aligned_inputs_2 = self.align(inputs_1, inputs_2)

        pairwise_equal = itertools.starmap(self.equality, zip(aligned_inputs_1, aligned_inputs_2))
        all_equal = functools.reduce(self.wire_and, pairwise_equal)

        return all_equal

    def shift(self, inputs_1: List[T], shifts: int) -> List[T]:
        return inputs_1 + [self.zero()] * shifts

    def align(self, inputs_1: List[T], inputs_2: List[T]) -> Tuple[List[T], List[T]]:
        aligned_inputs_1 = ([self.zero()] * (len(inputs_2) - len(inputs_1))) + inputs_1
        aligned_inputs_2 = ([self.zero()] * (len(inputs_1) - len(inputs_2))) + inputs_2

        return aligned_inputs_1, aligned_inputs_2
