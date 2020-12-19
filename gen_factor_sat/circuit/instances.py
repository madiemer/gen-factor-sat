from gen_factor_sat.circuit.default.circuit import Constant, ConstantStrategy, GeneralSimpleCircuitStrategy, \
    GeneralNBitCircuitStrategy
from gen_factor_sat.circuit.default.factoring import GeneralFactoringStrategy
from gen_factor_sat.circuit.default.multiplication import WallaceTreeStrategy, KaratsubaStrategy
from gen_factor_sat.circuit.tseitin.circuit import TseitinGateStrategy, CNFBuilder, TseitinCircuitStrategy
from gen_factor_sat.circuit.tseitin.encoding import Symbol


class TseitinFactoringStrategy(
    TseitinGateStrategy,
    TseitinCircuitStrategy,
    GeneralNBitCircuitStrategy[Symbol, CNFBuilder],
    KaratsubaStrategy[Symbol, CNFBuilder],
    WallaceTreeStrategy[Symbol, CNFBuilder],
    GeneralFactoringStrategy[Symbol, CNFBuilder]
):
    pass


class TseitinWallaceFactoringStrategy(
    TseitinGateStrategy,
    TseitinCircuitStrategy,
    GeneralNBitCircuitStrategy[Symbol, CNFBuilder],
    WallaceTreeStrategy[Symbol, CNFBuilder],
    GeneralFactoringStrategy[Symbol, CNFBuilder]
):
    pass


class ConstantFactoringStrategy(
    ConstantStrategy,
    GeneralSimpleCircuitStrategy[Constant, None],
    GeneralNBitCircuitStrategy[Constant, None],
    KaratsubaStrategy[Constant, None],
    WallaceTreeStrategy[Constant, None],
    GeneralFactoringStrategy[Constant, None]
):
    pass


class ConstantWallaceFactoringStrategy(
    ConstantStrategy,
    GeneralSimpleCircuitStrategy[Constant, None],
    GeneralNBitCircuitStrategy[Constant, None],
    WallaceTreeStrategy[Constant, None],
    GeneralFactoringStrategy[Constant, None]
):
    pass
