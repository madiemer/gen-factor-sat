import pytest
from pysat.formula import CNF
from pysat.solvers import Cadical

from gen_factor_sat.factoring_sat import factorize_number, factorize_random_number


def test_reproducibility():
    factoring_1 = factorize_random_number(213198414)
    factoring_2 = factorize_random_number(213198414)

    assert factoring_1 == factoring_2


@pytest.mark.parametrize("x", [2, 2 ** 10 + 659, 2 ** 15 + 5217])
@pytest.mark.parametrize("y", [2, 2 ** 10 + 561, 2 ** 15 + 1414])
def test_composite_number(x, y):
    print(bin(x))
    factor_sat = factorize_number(x * y)

    formula = CNF()
    formula.from_clauses(factor_sat.clauses)

    with Cadical(bootstrap_with=formula) as solver:
        assert solver.solve(), "The formula generated for a composite number should be in SAT"

        result_a = int(''.join(assignment_to_bin(factor_sat.factor_1, solver.get_model())), 2)
        result_b = int(''.join(assignment_to_bin(factor_sat.factor_2, solver.get_model())), 2)

        assert result_a * result_b == x * y, "Result a and b should contain all factors of x and y"


@pytest.mark.parametrize("prime", [2, 3, 5,
                                   1031,
                                   32771,  # < 2**20 => wallace_tree
                                   1073741827,  # > 2**20 => karatsuba
                                   # 1099511627791, #~ 2**40
                                   ])
def test_prime_number(prime):
    factor_sat = factorize_number(prime)

    formula = CNF()
    formula.from_clauses(factor_sat.clauses)

    with Cadical(bootstrap_with=formula) as solver:
        assert not solver.solve(), "The formula generated for a prime number should be in UNSAT"


def assignment_to_bin(sym, assignment):
    for s in sym:
        yield bin(assignment[s - 1] > 0)[2:]
