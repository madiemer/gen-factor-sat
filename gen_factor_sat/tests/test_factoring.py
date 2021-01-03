from collections import Counter

import pytest
from hypothesis import given, assume, settings
from hypothesis.strategies import integers, booleans, floats
from pysat.solvers import Solver

import gen_factor_sat.tests.utils as test_utils
from gen_factor_sat.factoring_sat import FactoringSat


@given(integers(min_value=2, max_value=2 ** 40))
@settings(deadline=None)
def test_reproducibility(number):
    factoring_1 = FactoringSat.factorize_number(number)
    factoring_2 = FactoringSat.factorize_number(number)

    assert factoring_1 == factoring_2, 'Multiple calls should yield the same result'


@given(
    max_value=integers(min_value=2, max_value=2 ** 40),
    min_value=integers(min_value=2, max_value=2 ** 20),
    seed=integers())
@settings(deadline=None)
def test_seeded_reproducibility(max_value, min_value, seed):
    assume(min_value <= max_value)
    factoring_1 = FactoringSat.factorize_random_number(max_value, min_value, seed)
    factoring_2 = FactoringSat.factorize_random_number(max_value, min_value, seed)

    assert factoring_1 == factoring_2, 'Multiple calls should yield the same result'


@given(
    max_value=integers(min_value=10, max_value=2 ** 40),
    min_value=integers(min_value=2, max_value=2 ** 10),
    seed=integers(),
    prime=booleans(),
    error=floats(min_value=0.0, max_value=1.0)
)
@settings(deadline=None)
def test_seeded_prime_reproducibility(max_value, min_value, seed, prime, error):
    assume(min_value <= max_value - 10)
    factoring_1 = FactoringSat.factorize_random_number(max_value, min_value, seed, prime, error)
    factoring_2 = FactoringSat.factorize_random_number(max_value, min_value, seed, prime, error)

    assert factoring_1 == factoring_2, 'Multiple calls should yield the same result'


@pytest.mark.parametrize("factor_1", [2, 2 ** 10 + 659, 2 ** 15 + 5217])
@pytest.mark.parametrize("factor_2", [2, 2 ** 10 + 561, 2 ** 15 + 1414])
def test_composite_number(factor_1, factor_2):
    factor_sat = FactoringSat.factorize_number(factor_1 * factor_2)

    with Solver(name='cadical', bootstrap_with=factor_sat.cnf.clauses) as solver:
        assert solver.solve(), "The formula generated for a composite number should be in SAT"

        for model in solver.enum_models():
            result_a = test_utils.assignment_to_int(factor_sat.factor_1, model)
            result_b = test_utils.assignment_to_int(factor_sat.factor_2, model)

            assert result_a != 1 and result_a != factor_1 * factor_2, "Factor 1 should be a non trivial factor"
            assert result_b != 1 and result_b != factor_1 * factor_2, "Factor 1 should be a non trivial factor"
            assert result_a * result_b == factor_1 * factor_2, "Result a and b should contain all factors of x and y"


@pytest.mark.parametrize(
    "prime",
    [2, 3, 5, 1031,
     32771,  # < 2**20 => wallace_tree
     1073741827,  # > 2**20 => karatsuba
     # 1099511627791, #~ 2**40
     ])
def test_prime_number(prime):
    factor_sat = FactoringSat.factorize_number(prime)

    with Solver(name='cadical', bootstrap_with=factor_sat.cnf.clauses) as solver:
        result = solver.solve()
        assert result is not None, "The solver should terminate"
        assert not result, "The formula generated for a prime number should be in UNSAT"


@given(integers(min_value=2, max_value=2 ** 25))
def test_clauses_have_no_duplicate_variables(number):
    factor_sat = FactoringSat.factorize_number(number)
    for clause in factor_sat.cnf.clauses:
        occurrences = Counter(clause)
        assert all(occurrences[literal] + occurrences[-literal] == 1 for literal in clause), \
            'A clause should not contain a variable twice'


@given(integers(min_value=2, max_value=2 ** 25))
def test_every_variable_should_occur_at_least_once(number):
    factor_sat = FactoringSat.factorize_number(number)

    variables = set()
    for clause in factor_sat.cnf.clauses:
        variables.update(map(abs, clause))

    assert len(variables) == factor_sat.cnf.number_of_variables, \
        'Every variable should occur at least once'

    assert all(variable <= factor_sat.cnf.number_of_variables for variable in variables), \
        'Variables should be numbered from 1 to the specified number'
