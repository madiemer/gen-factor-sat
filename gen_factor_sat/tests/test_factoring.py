import unittest

from hypothesis import given, settings, assume
from hypothesis.strategies import integers
from pysat.formula import CNF
from pysat.solvers import Cadical
from random import Random
from gen_factor_sat.factoring_sat import factoring_to_sat


class FactoringTest(unittest.TestCase):

    @given(integers(2, 2 ** 15), integers(2, 2 ** 15))
    @settings(deadline=None, max_examples=10)
    def test_composite_number(self, x, y):
        factor_sat = factoring_to_sat(x * y)

        formula = CNF()
        formula.from_clauses(factor_sat.clauses)
        solver = Cadical(bootstrap_with=formula)

        assert solver.solve(), "The formula generated for a composite number should be in SAT"

        result_a = int(''.join(FactoringTest.assignment_to_bin(factor_sat.factor_1, solver.get_model())), 2)
        result_b = int(''.join(FactoringTest.assignment_to_bin(factor_sat.factor_2, solver.get_model())), 2)

        assert result_a * result_b == x * y, "Result a and b should contain all factors of x and y"

    @given(integers(2, 2 ** 30))
    @settings(deadline=None, max_examples=10)
    def test_prime_number(self, n):
        FactoringTest.is_prime(n)
        assume(FactoringTest.is_prime(n))
        factor_sat = factoring_to_sat(2)

        formula = CNF()
        formula.from_clauses(factor_sat.clauses)
        solver = Cadical(bootstrap_with=formula)

        assert not solver.solve(), "The formula generated for a prime number should be in UNSAT"

    @staticmethod
    def assignment_to_bin(sym, assignment):
        for s in sym:
            yield bin(assignment[s - 1] > 0)[2:]

    @staticmethod
    def is_prime(number):
        return all(number % i for i in range(2, number))

    @staticmethod
    def primt(number):
        def run(a):
            d = 1
            dd = 1

            for b in bin(number - 1)[2:]:
                d = d * d % number
                if d == 1 and dd != 1 and dd != number - 1:
                    return False

                if b == '1':
                    d = d * a % number

                dd = d

            return d == 1

        rand = Random(1568915691591106)

        for i in range(1, 50):
            a = rand.randrange(1, number)
            if not run(a):
                return False

        return True
