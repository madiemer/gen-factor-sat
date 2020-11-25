import pytest
from hypothesis import given, assume
from hypothesis.strategies import integers
from pysat.formula import CNF
from pysat.solvers import Solver

from gen_factor_sat import strategies, utils
from gen_factor_sat.factoring_sat import multiply_to_cnf
from gen_factor_sat.multiplication import karatsuba, wallace_tree


@given(integers(0, 2 ** 40), integers(0, 2 ** 40))
def test_wallace(x, y):
    assert run_eval_mult(wallace_tree, x, y) == x * y


@given(integers(0, 2 ** 100), integers(0, 2 ** 100))
def test_karatsuba(x, y):
    assert run_eval_mult(karatsuba, x, y) == x * y


@given(integers(2 ** 70, 2 ** 100), integers(2 ** 20, 2 ** 50))
def test_split_simplification(x, y):
    assume(len(utils.to_bin_list(x)) > 2 * len(utils.to_bin_list(y)))
    assert run_eval_mult(karatsuba, x, y) == x * y


@pytest.mark.parametrize('factor_1', [1, 17, 2 ** 10 + 865, 2 * 21 + 46196])
@pytest.mark.parametrize('factor_2', [0, 2, 2 * 21 + 510579])
def test_tseitin_mult(factor_1, factor_2):
    assert run_tseitin_mult(karatsuba, factor_1, factor_2) == factor_1 * factor_2


def run_eval_mult(multiply, factor_1, factor_2):
    bin_factor_1 = utils.to_bin_list(factor_1)
    bin_factor_2 = utils.to_bin_list(factor_2)

    strategy = strategies.EvalStrategy()
    bin_result = multiply(bin_factor_1, bin_factor_2, strategy)

    return utils.to_int(bin_result)


def run_tseitin_mult(multiply, factor_1, factor_2):
    bin_factor_1 = utils.to_bin_list(factor_1)
    bin_factor_2 = utils.to_bin_list(factor_2)

    tseitin_strategy = strategies.TseitinStrategy()
    sym_factor_1, sym_factor_2, sym_result = multiply_to_cnf(multiply, len(bin_factor_1), len(bin_factor_2),
                                                             tseitin_strategy)

    assignment_1 = list(assign(sym_factor_1, bin_factor_1))
    assignment_2 = list(assign(sym_factor_2, bin_factor_2))

    bin_result = run_cnf(assignment_1 + assignment_2, sym_result, tseitin_strategy.clauses)

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
