from abc import ABC, abstractmethod
from typing import Sequence, Generic, TypeVar

from gen_factor_sat.circuit import NBitCircuitStrategy, ConstantStrategy, GeneralSimpleCircuitStrategy, \
    GeneralNBitCircuitStrategy
from gen_factor_sat.multiplication import MultiplicationStrategy, KaratsubaStrategy, WallaceTreeStrategy
from gen_factor_sat.tseitin_encoding import Symbol, Constant
from gen_factor_sat.tseitin_strategies import TseitinGateStrategy, CNFBuilder, TseitinCircuitStrategy

T = TypeVar('T')
W = TypeVar('W')


class FactoringCircuit(Generic[T, W], ABC):

    @abstractmethod
    def factorize(self, factor_1: Sequence[T], factor_2: Sequence[T], number: Sequence[T], writer: W) -> T:
        pass


class GeneralFactoringCircuit(
    Generic[T, W],
    NBitCircuitStrategy[T, W],
    MultiplicationStrategy[T, W],
    FactoringCircuit[T, W],
    ABC
):
    def factorize(self, factor_1: Sequence[T], factor_2: Sequence[T], number: Sequence[T], writer: W) -> T:
        mult_result = self.multiply(factor_1, factor_2, writer)
        fact_result = self.n_bit_equality(mult_result, number, writer)
        return fact_result


class TseitinFactoringStrategy(
    TseitinGateStrategy,
    TseitinCircuitStrategy,
    GeneralNBitCircuitStrategy[Symbol, CNFBuilder],
    WallaceTreeStrategy[Symbol, CNFBuilder],
    KaratsubaStrategy[Symbol, CNFBuilder],
    GeneralFactoringCircuit[Symbol, CNFBuilder]
):
    pass


class ConstantFactoringStrategy(
    ConstantStrategy,
    GeneralSimpleCircuitStrategy[Constant, None],
    GeneralNBitCircuitStrategy[Constant, None],
    WallaceTreeStrategy[Constant, None],
    KaratsubaStrategy[Constant, None],
    GeneralFactoringCircuit[Constant, None]
):
    pass
