import collections
import functools
import itertools
from typing import List, Tuple, DefaultDict, Iterable

from gen_factor_sat.circuit import NBitCircuit
from gen_factor_sat.strategies import Strategy, T


class Multiplication:
    def __init__(self, *args, **kwargs):
        super(Multiplication, self).__init__(*args, **kwargs)
    
    def multiply(self, factor_1: List[T], factor_2: List[T]) -> List[T]:
        pass


class KaratsubaMultiplication(Multiplication, NBitCircuit[T]):

    def __init__(self, simple_mult, min_len=20, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.simple_mult = simple_mult
        self.min_len = min_len

    def multiply(self, factor_1: List[T], factor_2: List[T]) -> List[T]:
        max_factor_length = max(len(factor_1), len(factor_2))

        if max_factor_length <= self.min_len:
            return self.simple_mult.multiply(factor_1, factor_2)
        else:
            half_factor_length = (max_factor_length + 1) // 2

            f1_high, f1_low = split_at(factor_1, -half_factor_length)
            f2_high, f2_low = split_at(factor_2, -half_factor_length)

            result_low = self.multiply(f1_low, f2_low)
            result_high = self.multiply(f1_high, f2_high)

            # result_mid = karatsuba((f1_high + f1_low), (f2_high + f2_low)) - result_high - result_low
            factor_1_sum = self.n_bit_adder(f1_high, f1_low, self.zero())
            factor_2_sum = self.n_bit_adder(f2_high, f2_low, self.zero())

            result_mid = self.multiply(factor_1_sum, factor_2_sum)
            result_mid = self.subtract(result_mid, result_high)
            result_mid = self.subtract(result_mid, result_low)

            # result = result_high * 2^(2 * half_factor_length) + result_mid * 2^(half_factor_length) + result_low
            shifted_high = self.shift(result_high, half_factor_length)
            result = self.n_bit_adder(shifted_high, result_mid, self.zero())

            shifted_high = self.shift(result, half_factor_length)
            result = self.n_bit_adder(shifted_high, result_low, self.zero())

            return result


class WallaceTreeMultiplier(Multiplication, NBitCircuit[T]):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tset = "atrat"

    def multiply(self, factor_1: List[T], factor_2: List[T]) -> List[T]:
        products = self._weighted_product(factor_1, factor_2)
        grouped_products = self._group(products)

        while any(len(xs) > 2 for _, xs in grouped_products.items()):
            products = itertools.chain.from_iterable(
                itertools.starmap(self._add_layer, grouped_products.items())
            )

            grouped_products = self._group(products)

        result = []
        last_carry = self.zero()
        for key in sorted(grouped_products):
            products = grouped_products[key]

            if len(products) == 1:
                x, = products
                sum, carry = self.half_adder(x, last_carry)
                last_carry = carry
                result.append(sum)
            else:
                x, y = products
                sum, carry = self.full_adder(x, y, last_carry)
                last_carry = carry
                result.append(sum)

        result.append(last_carry)
        return result[::-1]


    def _weighted_product(self, factor_1: List[T], factor_2: List[T]):
        for i, x in enumerate(factor_1):
            w_x = len(factor_1) - i

            for j, y in enumerate(factor_2):
                w_y = len(factor_2) - j

                weight_sum = w_x + w_y
                product = self.wire_and(x, y)

                yield weight_sum, product


    def _add_layer(self, weight: int, products: List[T]) -> List[Tuple[int, T]]:
        if len(products) == 1:
            return [(weight, products[0])]

        elif len(products) == 2:
            x, y = products
            sum, carry = self.half_adder(x, y)

            return [(weight, sum), (weight + 1, carry)]

        elif len(products) > 2:
            x, y, z = products[:3]
            sum, carry = self.full_adder(x, y, z)

            return [(weight, sum), (weight + 1, carry)] + [(weight, x) for x in products[3:]]

        else:
            raise ValueError('Cannot add a layer for an empty product')


    def _group(self, iterable: Iterable[Tuple[int, T]]) -> DefaultDict[int, List[T]]:
        result = collections.defaultdict(list)
        for key, value in iterable:
            result[key].append(value)

        return result


def split_at(list, index):
    return list[:index], list[index:]
