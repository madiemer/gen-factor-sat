import pytest
from hypothesis import given, example
from hypothesis.strategies import integers
from pysat.formula import CNF
from pysat.solvers import Cadical

from gen_factor_sat import utils
from gen_factor_sat.factoring_sat import factorize_number, _generate_number


@given(integers(1, 2 ** 40))
def test_reproducibility(number):
    factoring_1 = factorize_number(number)
    factoring_2 = factorize_number(number)

    assert factoring_1 == factoring_2


@given(integers())
@example(0)
@example(1)
@example(-1)
def test_seeded_reproducibility(seed):
    number_1 = _generate_number(seed)
    number_2 = _generate_number(seed)

    assert number_1 == number_2


@pytest.mark.parametrize("x", [2, 2 ** 10 + 659, 2 ** 15 + 5217])
@pytest.mark.parametrize("y", [2, 2 ** 10 + 561, 2 ** 15 + 1414])
def test_composite_number(x, y):
    factor_sat = factorize_number(x * y)
    formula = CNF(from_clauses=factor_sat.clauses)

    with Cadical(bootstrap_with=formula) as solver:
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

    with Cadical(bootstrap_with=formula) as solver:
        assert not solver.solve(), "The formula generated for a prime number should be in UNSAT"


def assignment_to_int(sym, assignment):
    return utils.to_int(list(assignment_to_bin(sym, assignment)))


def assignment_to_bin(sym, assignment):
    for s in sym:
        yield utils.to_bin_string(assignment[s - 1] > 0)
