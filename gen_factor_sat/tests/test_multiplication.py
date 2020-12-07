import pytest
from hypothesis import given, assume
from hypothesis.strategies import integers
from pysat.formula import CNF
from pysat.solvers import Solver

from gen_factor_sat import utils
from gen_factor_sat.circuit import ConstantStrategy, GeneralSimpleCircuitStrategy, GeneralNBitCircuitStrategy
from gen_factor_sat.multiplier import KaratsubaMultiplier, WallaceTreeMultiplier
from gen_factor_sat.tseitin_strategies import CNFBuilder, TseitinGateStrategy, TseitinCircuitStrategy

@pytest.fixture(scope='module')
def constant_wallace_tree():
    gate_strategy = ConstantStrategy()
    simple_circuit = GeneralSimpleCircuitStrategy(gate_strategy=gate_strategy)
    wallace_mult = WallaceTreeMultiplier(gate_strategy=gate_strategy, simple_circuit=simple_circuit)

    return wallace_mult


@pytest.fixture(scope='module')
def constant_karatsuba():
    gate_strategy = ConstantStrategy()
    simple_circuit = GeneralSimpleCircuitStrategy(gate_strategy=gate_strategy)
    n_bit_circuit = GeneralNBitCircuitStrategy(gate_strategy=gate_strategy, circuit_strategy=simple_circuit)
    wallace_mult = WallaceTreeMultiplier(gate_strategy=gate_strategy, simple_circuit=simple_circuit)
    karatsuba = KaratsubaMultiplier(gate_strategy=gate_strategy,
                                    n_bit_circuit=n_bit_circuit,
                                    simple_multiplier=wallace_mult)

    return karatsuba

@pytest.fixture(scope='module')
def create_tseitin_karatsuba():
    def _create_tseitin_karatsuba(cnf_builder):
        gate_strategy = TseitinGateStrategy(cnf_builder)

        simple_circuit = TseitinCircuitStrategy(
            cnf_builder=cnf_builder,
            gate_strategy=gate_strategy
        )

        n_bit_circuit = GeneralNBitCircuitStrategy(
            gate_strategy=gate_strategy,
            circuit_strategy=simple_circuit
        )

        wallace_mult = WallaceTreeMultiplier(
            gate_strategy=gate_strategy,
            simple_circuit=simple_circuit
        )

        karatsuba = KaratsubaMultiplier(
            gate_strategy=gate_strategy,
            n_bit_circuit=n_bit_circuit,
            simple_multiplier=wallace_mult
        )

        return karatsuba

    return _create_tseitin_karatsuba

@given(x=integers(0, 2 ** 40), y=integers(0, 2 ** 40))
def test_wallace(constant_wallace_tree, x, y):
    assert run_eval_mult(constant_wallace_tree, x, y) == x * y


@given(x=integers(0, 2 ** 60), y=integers(0, 2 ** 60))
def test_karatsuba(constant_karatsuba, x, y):
    assert run_eval_mult(constant_karatsuba, x, y) == x * y


@given(x=integers(2 ** 21, 2 ** 60), y=integers(0, 2 ** 30))
def test_split_simplification(constant_karatsuba, x, y):
    assume(len(utils.to_bin_list(x)) > 2 * len(utils.to_bin_list(y)))
    assert run_eval_mult(constant_karatsuba, x, y) == x * y


@pytest.mark.parametrize('factor_1', [1, 17, 2 ** 10 + 865, 2 * 21 + 46196])
@pytest.mark.parametrize('factor_2', [0, 2, 2 * 21 + 510579])
def test_tseitin_mult(create_tseitin_karatsuba, factor_1, factor_2):
    assert run_tseitin_mult(create_tseitin_karatsuba, factor_1, factor_2) == factor_1 * factor_2


def run_eval_mult(multiplier, factor_1, factor_2):
    bin_factor_1 = utils.to_bin_list(factor_1)
    bin_factor_2 = utils.to_bin_list(factor_2)

    bin_result = multiplier.multiply(bin_factor_1, bin_factor_2)

    return utils.to_int(bin_result)


def run_tseitin_mult(tseitin_multiplier, factor_1, factor_2):
    cnf_builder = CNFBuilder()
    multiplier = tseitin_multiplier(cnf_builder)

    bin_factor_1 = utils.to_bin_list(factor_1)
    bin_factor_2 = utils.to_bin_list(factor_2)

    factor_1 = cnf_builder.next_variables(len(bin_factor_1))
    factor_2 = cnf_builder.next_variables(len(bin_factor_2))

    result = multiplier.multiply(factor_1, factor_2)

    assignment_1 = list(assign(factor_1, bin_factor_1))
    assignment_2 = list(assign(factor_2, bin_factor_2))

    bin_result = run_cnf(assignment_1 + assignment_2, result, cnf_builder.clauses)

    return utils.to_int(bin_result)


def assign(variables, values):
    for variable, value in zip(variables, values):
        yield variable if value == '1' else -variable


def run_cnf(input_assignment, output_variables, clauses):
    formula = CNF(from_clauses=clauses)

    with Solver(name="cadical", bootstrap_with=formula) as solver:
        solver.solve(assumptions=input_assignment)
        model = solver.get_model()

    result_assign = [(model[r - 1] >= 0 if r != '0' else False) for r in output_variables]
    return list(map(utils.to_bin_string, result_assign))
