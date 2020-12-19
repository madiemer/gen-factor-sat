from abc import ABC
from typing import List, Generic, TypeVar

from gen_factor_sat.circuit.interface.circuit import NBitCircuitStrategy
from gen_factor_sat.circuit.interface.factoring import FactoringStrategy
from gen_factor_sat.circuit.interface.multiplication import RecursiveMultiplicationStrategy

T = TypeVar('T')
W = TypeVar('W')


class GeneralFactoringStrategy(
    Generic[T, W],
    NBitCircuitStrategy[T, W],
    RecursiveMultiplicationStrategy[T, W],
    FactoringStrategy[T, W],
    ABC
):
    def factorize(self, factor_1: List[T], factor_2: List[T], number: List[T], writer: W) -> T:
        mult_result = self.multiply_recursive(factor_1, factor_2, writer)
        fact_result = self.n_bit_equality(mult_result, number, writer)
        return fact_result
