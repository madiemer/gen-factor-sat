from collections import Counter

import pytest
from hypothesis import given
from hypothesis.strategies import integers
from pysat.formula import CNF
from pysat.solvers import Solver

from gen_factor_sat import utils
from gen_factor_sat.factoring_sat import factorize_number, factorize_random_number


@given(integers(min_value=2, max_value=2 ** 40))
def test_reproducibility(number):
    factoring_1 = factorize_number(number)
    factoring_2 = factorize_number(number)

    assert factoring_1 == factoring_2


@given(integers(min_value=2, max_value=2 ** 40), integers())
def test_seeded_reproducibility(max_value, seed):
    number_1 = factorize_random_number(max_value, seed)
    number_2 = factorize_random_number(max_value, seed)

    assert number_1 == number_2


@pytest.mark.parametrize("x", [2, 2 ** 10 + 659, 2 ** 15 + 5217])
@pytest.mark.parametrize("y", [2, 2 ** 10 + 561, 2 ** 15 + 1414])
def test_composite_number(x, y):
    factor_sat = factorize_number(x * y)
    formula = CNF(from_clauses=factor_sat.clauses)

    with Solver(name='cadical', bootstrap_with=formula) as solver:
        assert solver.solve(), "The formula generated for a composite number should be in SAT"

        model = solver.get_model()
        result_a = assignment_to_int(factor_sat.factor_1, model)
        result_b = assignment_to_int(factor_sat.factor_2, model)

        assert result_a * result_b == x * y, "Result a and b should contain all factors of x and y"


@pytest.mark.parametrize(
    "prime",
    [2, 3, 5, 1031,
     32771,  # < 2**20 => wallace_tree
     1073741827,  # > 2**20 => karatsuba
     # 1099511627791, #~ 2**40
     ])
def test_prime_number(prime):
    factor_sat = factorize_number(prime)
    formula = CNF(from_clauses=factor_sat.clauses)

    with Solver(name='cadical', bootstrap_with=formula) as solver:
        result = solver.solve()
        assert result is not None, "The solver should terminate"
        assert not result, "The formula generated for a prime number should be in UNSAT"


@given(integers(min_value=2, max_value=2 ** 25))
def test_clauses_have_no_duplicate_variables(number):
    factor_sat = factorize_number(number)
    for clause in factor_sat.clauses:
        occurrences = Counter(clause)
        assert all(occurrences[-literal] == 0 for literal in clause)
        assert all(occurrences[literal] == 1 for literal in clause)


@given(integers(min_value=2, max_value=2 ** 25))
def test_every_variable_should_occur_at_least_once(number):
    factor_sat = factorize_number(number)

    variables = set()
    for clause in factor_sat.clauses:
        variables.update(map(abs, clause))

    assert len(variables) == factor_sat.number_of_variables, 'Every variable should occur at least once'
    assert all(x <= factor_sat.number_of_variables for x in
               variables), 'Variables should be numbered from 1 to the specified number'


def assignment_to_int(sym, assignment):
    return utils.to_int(list(assignment_to_bin(sym, assignment)))


def assignment_to_bin(sym, assignment):
    for s in sym:
        yield utils.to_bin_string(assignment[s - 1] > 0)
