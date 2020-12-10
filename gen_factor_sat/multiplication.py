import functools
import itertools
from abc import ABC, abstractmethod
from typing import Sequence, Tuple, Generic, TypeVar

from gen_factor_sat import utils
from gen_factor_sat.circuit import GateStrategy, SimpleCircuitStrategy, NBitCircuitStrategy

T = TypeVar('T')
W = TypeVar('W')


class MultiplicationStrategy(Generic[T, W], ABC):

    @abstractmethod
    def multiply(self, factor_1: Sequence[T], factor_2: Sequence[T], writer: W = None) -> Sequence[T]:
        pass


class RecursiveMultiplicationStrategy(Generic[T, W], MultiplicationStrategy[T, W], ABC):

    @abstractmethod
    def multiply_recursive(self, factor_1: Sequence[T], factor_2: Sequence[T], writer: W = None) -> Sequence[T]:
        pass


class KaratsubaStrategy(
    Generic[T, W],
    GateStrategy[T, W],
    NBitCircuitStrategy[T, W],
    RecursiveMultiplicationStrategy[T, W],
    ABC
):
    min_len: int = 20

    def multiply_recursive(self, factor_1: Sequence[T], factor_2: Sequence[T], writer: W = None) -> Sequence[T]:
        max_factor_length = max(len(factor_1), len(factor_2))

        if max_factor_length <= self.min_len:
            return self.multiply(factor_1, factor_2, writer)
        else:
            half_factor_length = (max_factor_length + 1) // 2

            f1_high, f1_low = utils.split_at(factor_1, -half_factor_length)
            f2_high, f2_low = utils.split_at(factor_2, -half_factor_length)

            result_low = self.multiply(f1_low, f2_low, writer)
            result_high = self.multiply(f1_high, f2_high, writer)

            # result_mid = karatsuba((f1_high + f1_low), (f2_high + f2_low)) - result_high - result_low
            factor_1_sum = self.n_bit_adder(f1_high, f1_low, self.zero, writer)
            factor_2_sum = self.n_bit_adder(f2_high, f2_low, self.zero, writer)

            result_mid = self.multiply(factor_1_sum, factor_2_sum, writer)
            result_mid = self.subtract(result_mid, result_high, writer)
            result_mid = self.subtract(result_mid, result_low, writer)

            # result = result_high * 2^(2 * half_factor_length) + result_mid * 2^(half_factor_length) + result_low
            shifted_high = self.shift(result_high, half_factor_length, writer)
            result = self.n_bit_adder(shifted_high, result_mid, self.zero, writer)

            shifted_high = self.shift(result, half_factor_length, writer)
            result = self.n_bit_adder(shifted_high, result_low, self.zero, writer)

            return result


class WallaceTreeStrategy(
    Generic[T, W],
    GateStrategy[T, W],
    SimpleCircuitStrategy[T, W],
    MultiplicationStrategy[T, W],
    ABC
):

    def multiply(self, factor_1: Sequence[T], factor_2: Sequence[T], writer: W = None) -> Sequence[T]:
        products = self._weighted_product(factor_1, factor_2, writer)
        grouped_products = utils.group(products)

        while any(len(xs) > 2 for _, xs in grouped_products.items()):
            products = itertools.chain.from_iterable(
                itertools.starmap(functools.partial(self._add_layer, writer=writer), grouped_products.items())
            )

            grouped_products = utils.group(products)

        result = []
        last_carry = self.zero
        for key in sorted(grouped_products):
            products = grouped_products[key]

            if len(products) == 1:
                x, = products
                sum, carry = self.half_adder(x, last_carry, writer)
                last_carry = carry
                result.append(sum)
            else:
                x, y = products
                sum, carry = self.full_adder(x, y, last_carry, writer)
                last_carry = carry
                result.append(sum)

        result.append(last_carry)
        return result[::-1]

    def _weighted_product(self, factor_1: Sequence[T], factor_2: Sequence[T], writer: W):
        for i, x in enumerate(factor_1):
            w_x = len(factor_1) - i

            for j, y in enumerate(factor_2):
                w_y = len(factor_2) - j

                weight_sum = w_x + w_y
                product = self.wire_and(x, y, writer)

                yield weight_sum, product

    def _add_layer(self, weight: int, products: Sequence[T], writer: W) -> Sequence[Tuple[int, T]]:
        if len(products) == 1:
            return [(weight, products[0])]

        elif len(products) == 2:
            x, y = products
            sum, carry = self.half_adder(x, y, writer)

            return [(weight, sum), (weight + 1, carry)]

        elif len(products) > 2:
            x, y, z = products[:3]
            sum, carry = self.full_adder(x, y, z, writer)

            return [(weight, sum), (weight + 1, carry)] + [(weight, x) for x in products[3:]]

        else:
            raise ValueError('Cannot add a layer for an empty product')
