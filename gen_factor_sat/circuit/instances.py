from abc import ABC
from typing import TypeVar

from gen_factor_sat.circuit.default.circuit import ConstantStrategy, GeneralSimpleCircuitStrategy, \
    GeneralNBitCircuitStrategy
from gen_factor_sat.circuit.default.factoring import GeneralFactoringStrategy
from gen_factor_sat.circuit.default.multiplication import WallaceTreeStrategy, KaratsubaStrategy
from gen_factor_sat.circuit.interface.circuit import GateStrategy
from gen_factor_sat.circuit.interface.factoring import FactoringStrategy
from gen_factor_sat.circuit.tseitin.circuit import TseitinGateStrategy, TseitinCircuitStrategy
from gen_factor_sat.formula.cnf import CNFBuilder
from gen_factor_sat.formula.symbol import Symbol, Constant

T = TypeVar('T')
W = TypeVar('W')


class FactoringAndGateStrategy(
    GateStrategy[T, W],
    FactoringStrategy[T, W],
    ABC
):
    """
    Interface to specify the required mixin type for FactoringSat. Future
    versions will use protocols and remove the necessity to actively inherit
    from this interface.
    """
    pass


class TseitinFactoringStrategy(
    TseitinGateStrategy,
    TseitinCircuitStrategy,
    GeneralNBitCircuitStrategy[Symbol, CNFBuilder],
    KaratsubaStrategy[Symbol, CNFBuilder],
    WallaceTreeStrategy[Symbol, CNFBuilder],
    GeneralFactoringStrategy[Symbol, CNFBuilder],
    FactoringAndGateStrategy[Symbol, CNFBuilder]
):
    pass


class TseitinWallaceFactoringStrategy(
    TseitinGateStrategy,
    TseitinCircuitStrategy,
    GeneralNBitCircuitStrategy[Symbol, CNFBuilder],
    WallaceTreeStrategy[Symbol, CNFBuilder],
    GeneralFactoringStrategy[Symbol, CNFBuilder],
    FactoringAndGateStrategy[Symbol, CNFBuilder]
):
    pass


class ConstantFactoringStrategy(
    ConstantStrategy,
    GeneralSimpleCircuitStrategy[Constant, None],
    GeneralNBitCircuitStrategy[Constant, None],
    KaratsubaStrategy[Constant, None],
    WallaceTreeStrategy[Constant, None],
    GeneralFactoringStrategy[Constant, None],
    FactoringAndGateStrategy[Constant, None]
):
    pass


class ConstantWallaceFactoringStrategy(
    ConstantStrategy,
    GeneralSimpleCircuitStrategy[Constant, None],
    GeneralNBitCircuitStrategy[Constant, None],
    WallaceTreeStrategy[Constant, None],
    GeneralFactoringStrategy[Constant, None],
    FactoringAndGateStrategy[Constant, None]
):
    pass
