import unittest

from hypothesis import given, settings, assume
from hypothesis.strategies import integers
from pysat.formula import CNF
from pysat.solvers import Glucose4
import time

from FactorSat import factoring_to_sat


class FactoringTest(unittest.TestCase):

    @given(integers(2, 2 ** 30), integers(2, 2 ** 30))
    @settings(deadline=None)
    def test_composite_number(self, x, y):
        start = time.time_ns()
        factor_sat = factoring_to_sat(x * y)
        end = time.time_ns()
        print(str(x * y) + ' ' + str(end - start))

        formula = CNF()
        formula.from_clauses(factor_sat.clauses)
        solver = Glucose4(bootstrap_with=formula)

        assert solver.solve(), "The formula generated for a composite number should be in SAT"

        result_a = int(''.join(FactoringTest.assignment_to_bin(factor_sat.factor_1, solver.get_model())), 2)
        result_b = int(''.join(FactoringTest.assignment_to_bin(factor_sat.factor_2, solver.get_model())), 2)

        assert result_a * result_b == x * y, "Result a and b should contain all factors of x and y"

    # @given(integers(5, 2 ** 30))
    # @settings(deadline=None)
    # def test_prime_number(self, n):
    #     assume(FactoringTest.is_prime(n))
    #     factor_sat = factoring_to_sat(n)
    #
    #     formula = CNF()
    #     formula.from_clauses(factor_sat.clauses)
    #     solver = Glucose4(bootstrap_with=formula)
    #
    #     assert not solver.solve(), "The formula generated for a prime number should be in UNSAT"


    @staticmethod
    def assignment_to_bin(sym, assignment):
        for s in sym:
            yield bin(assignment[s - 1] > 0)[2:]

    @staticmethod
    def is_prime(number):
        return all(number % i for i in range(2, number))
