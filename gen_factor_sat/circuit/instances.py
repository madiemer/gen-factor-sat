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
    WallaceTreeStrategy[Symbol, CNFBuilder],
    KaratsubaStrategy[Symbol, CNFBuilder],
    GeneralFactoringStrategy[Symbol, CNFBuilder]
):
    pass


class ConstantFactoringStrategy(
    ConstantStrategy,
    GeneralSimpleCircuitStrategy[Constant, None],
    GeneralNBitCircuitStrategy[Constant, None],
    WallaceTreeStrategy[Constant, None],
    KaratsubaStrategy[Constant, None],
    GeneralFactoringStrategy[Constant, None]
):
    pass
