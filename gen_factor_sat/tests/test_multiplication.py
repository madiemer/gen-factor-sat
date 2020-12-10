import pytest
from hypothesis import given, assume
from hypothesis.strategies import integers
from pysat.formula import CNF
from pysat.solvers import Solver

from gen_factor_sat import utils
from gen_factor_sat.circuit import ConstantStrategy, GeneralSimpleCircuitStrategy, GeneralNBitCircuitStrategy
from gen_factor_sat.factoring_sat import ConstantFactoringStrategy, TseitinFactoringStrategy
from gen_factor_sat.multiplication import KaratsubaStrategy, WallaceTreeStrategy
from gen_factor_sat.tseitin_strategies import CNFBuilder, Constant

@pytest.fixture(scope='module')
def constant_strategy():
    return ConstantFactoringStrategy()

@pytest.fixture(scope='module')
def tseitin_strategy():
    return TseitinFactoringStrategy()

@given(x=integers(0, 2 ** 40), y=integers(0, 2 ** 40))
def test_wallace(constant_strategy, x, y):
    assert run_eval_mult(constant_strategy.multiply, x, y) == x * y


@given(x=integers(0, 2 ** 60), y=integers(0, 2 ** 60))
def test_karatsuba(constant_strategy, x, y):
    assert run_eval_mult(constant_strategy.multiply_recursive, x, y) == x * y


@given(x=integers(2 ** 21, 2 ** 60), y=integers(0, 2 ** 30))
def test_split_simplification(constant_strategy, x, y):
    assume(len(utils.to_bin_list(x)) > 2 * len(utils.to_bin_list(y)))
    assert run_eval_mult(constant_strategy.multiply_recursive, x, y) == x * y


@pytest.mark.parametrize('factor_1', [1, 17, 2 ** 10 + 865, 2 * 21 + 46196])
@pytest.mark.parametrize('factor_2', [0, 2, 2 * 21 + 510579])
def test_tseitin_mult(tseitin_strategy, factor_1, factor_2):
    assert run_tseitin_mult(tseitin_strategy.multiply_recursive, factor_1, factor_2) == factor_1 * factor_2


def run_eval_mult(multiply, factor_1, factor_2):
    bin_factor_1 = utils.to_bin_list(factor_1)
    bin_factor_2 = utils.to_bin_list(factor_2)

    bin_result = multiply(bin_factor_1, bin_factor_2)

    return utils.to_int(bin_result)


def run_tseitin_mult(tseitin_multiplier, factor_1, factor_2):
    cnf_builder = CNFBuilder()

    bin_factor_1 = utils.to_bin_list(factor_1)
    bin_factor_2 = utils.to_bin_list(factor_2)

    factor_1 = cnf_builder.next_variables(len(bin_factor_1))
    factor_2 = cnf_builder.next_variables(len(bin_factor_2))

    result = tseitin_multiplier(factor_1, factor_2, cnf_builder)

    assignment_1 = list(assign(factor_1, bin_factor_1))
    assignment_2 = list(assign(factor_2, bin_factor_2))

    bin_result = run_cnf(assignment_1 + assignment_2, result, cnf_builder._clauses)

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
