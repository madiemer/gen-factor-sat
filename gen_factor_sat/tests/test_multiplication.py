import pytest
from hypothesis import given, assume
from hypothesis.strategies import integers
from pysat.formula import CNF
from pysat.solvers import Solver

from gen_factor_sat import strategies
from gen_factor_sat.factoring_sat import create_symbolic_input
from gen_factor_sat.multiplication import karatsuba, wallace_tree


@given(integers(0, 2 ** 40), integers(0, 2 ** 40))
def test_wallace(x, y):
    assert run_eval(x, y, wallace_tree) == x * y


@given(integers(0, 2 ** 100), integers(0, 2 ** 100))
def test_karatsuba(x, y):
    assert run_eval(x, y, karatsuba) == x * y


@given(integers(2 ** 70, 2 ** 100), integers(2 ** 20, 2 ** 50))
def test_split_simplification(x, y):
    assume(len(bin(x)[2:]) > 2 * len(bin(y)[2:]))
    assert run_eval(x, y, karatsuba) == x * y


@pytest.mark.parametrize('x', [1, 17, 2 ** 10 + 865, 2 * 20 + 46196])
@pytest.mark.parametrize('y', [0, 2, 2 * 20 + 510579])
def test_tseitin_mult(x, y):
    assert run_cnf(x, y, karatsuba) == x * y


def run_eval(x, y, func):
    bin_x = bin(y)[2:]
    bin_y = bin(x)[2:]

    strategy = strategies.EvalStrategy()
    result = func(bin_x, bin_y, strategy)

    bin_result = ''.join(result)
    return int(bin_result, 2)


def run_cnf(x, y, func):
    bin_x = bin(x)[2:]
    bin_y = bin(y)[2:]

    sym_x, sym_y = create_symbolic_input(len(bin_x), len(bin_y))
    tseitin_strategy = strategies.TseitinStrategy(sym_x + sym_y)
    result = func(sym_x, sym_y, tseitin_strategy)

    formula = CNF(from_clauses=tseitin_strategy.clauses)

    assignment = []
    for x, a in zip(sym_x, bin_x):
        assignment.append(x if a == '1' else -x)

    for y, a in zip(sym_y, bin_y):
        assignment.append(y if a == '1' else -y)

    with Solver(name="cadical", bootstrap_with=formula) as solver:
        solver.solve(assumptions=assignment)
        model = solver.get_model()

    result_assign = [(model[r - 1] >= 0 if r != '0' else False) for r in result]
    return int(''.join(list(map(lambda x: bin(x)[2:], result_assign))), 2)
