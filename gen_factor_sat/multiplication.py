import itertools
from typing import List, Tuple, Generic

from gen_factor_sat import utils
from gen_factor_sat.circuit import T, GateStrategy, CircuitStrategy, NBitCircuitStrategy


class Multiplication(Generic[T]):

    def multiply(self, factor_1: List[T], factor_2: List[T]) -> List[T]:
        pass


class KaratsubaMultiplication(Multiplication):

    def __init__(self,
                 gate_strategy: GateStrategy[T],
                 n_bit_circuit: NBitCircuitStrategy[T],
                 simple_multiplication: Multiplication[T],
                 min_len=20):
        self.circuit = gate_strategy
        self.n_bit_circuit = n_bit_circuit
        self.simple_multiplication = simple_multiplication
        self.min_len = min_len

    def multiply(self, factor_1: List[T], factor_2: List[T]) -> List[T]:
        max_factor_length = max(len(factor_1), len(factor_2))

        if max_factor_length <= self.min_len:
            return self.simple_multiplication.multiply(factor_1, factor_2)
        else:
            half_factor_length = (max_factor_length + 1) // 2

            f1_high, f1_low = utils.split_at(factor_1, -half_factor_length)
            f2_high, f2_low = utils.split_at(factor_2, -half_factor_length)

            result_low = self.multiply(f1_low, f2_low)
            result_high = self.multiply(f1_high, f2_high)

            # result_mid = karatsuba((f1_high + f1_low), (f2_high + f2_low)) - result_high - result_low
            factor_1_sum = self.n_bit_circuit.n_bit_adder(f1_high, f1_low, self.circuit.zero())
            factor_2_sum = self.n_bit_circuit.n_bit_adder(f2_high, f2_low, self.circuit.zero())

            result_mid = self.multiply(factor_1_sum, factor_2_sum)
            result_mid = self.n_bit_circuit.subtract(result_mid, result_high)
            result_mid = self.n_bit_circuit.subtract(result_mid, result_low)

            # result = result_high * 2^(2 * half_factor_length) + result_mid * 2^(half_factor_length) + result_low
            shifted_high = self.n_bit_circuit.shift(result_high, half_factor_length)
            result = self.n_bit_circuit.n_bit_adder(shifted_high, result_mid, self.circuit.zero())

            shifted_high = self.n_bit_circuit.shift(result, half_factor_length)
            result = self.n_bit_circuit.n_bit_adder(shifted_high, result_low, self.circuit.zero())

            return result


class WallaceTreeMultiplier(Multiplication):

    def __init__(self, gate_strategy: GateStrategy[T], simple_circuit: CircuitStrategy[T]):
        self.gate_strategy = gate_strategy
        self.simple_circuit = simple_circuit

    def multiply(self, factor_1: List[T], factor_2: List[T]) -> List[T]:
        products = self._weighted_product(factor_1, factor_2)
        grouped_products = utils.group(products)

        while any(len(xs) > 2 for _, xs in grouped_products.items()):
            products = itertools.chain.from_iterable(
                itertools.starmap(self._add_layer, grouped_products.items())
            )

            grouped_products = utils.group(products)

        result = []
        last_carry = self.gate_strategy.zero()
        for key in sorted(grouped_products):
            products = grouped_products[key]

            if len(products) == 1:
                x, = products
                sum, carry = self.simple_circuit.half_adder(x, last_carry)
                last_carry = carry
                result.append(sum)
            else:
                x, y = products
                sum, carry = self.simple_circuit.full_adder(x, y, last_carry)
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
                product = self.gate_strategy.wire_and(x, y)

                yield weight_sum, product

    def _add_layer(self, weight: int, products: List[T]) -> List[Tuple[int, T]]:
        if len(products) == 1:
            return [(weight, products[0])]

        elif len(products) == 2:
            x, y = products
            sum, carry = self.simple_circuit.half_adder(x, y)

            return [(weight, sum), (weight + 1, carry)]

        elif len(products) > 2:
            x, y, z = products[:3]
            sum, carry = self.simple_circuit.full_adder(x, y, z)

            return [(weight, sum), (weight + 1, carry)] + [(weight, x) for x in products[3:]]

        else:
            raise ValueError('Cannot add a layer for an empty product')