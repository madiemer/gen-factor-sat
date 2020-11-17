import unittest

from hypothesis import given, settings, assume
from hypothesis.strategies import integers

from pysat.solvers import Glucose3
from pysat.formula import CNF

from SATGenerator import factoring_to_sat


class FactoringTest(unittest.TestCase):

    @given(integers(2, 10 ** 20), integers(2, 10 ** 20))
    def test_composite_number(self, x, y):
        sym_x, sym_y, variable, clauses = factoring_to_sat(x * y)

        cnf = FactoringTest.cnf_to_pysat(clauses)
        solver = Glucose3(bootstrap_with=cnf)

        assert solver.solve(), "The formula generated for a composite number should be in SAT"

        result_a = int(''.join(FactoringTest.assignment_to_bin(sym_x, solver.get_model())), 2)
        result_b = int(''.join(FactoringTest.assignment_to_bin(sym_y, solver.get_model())), 2)

        assert result_a * result_b == x * y, "Result a and b should contain all factors of x and y"

    @given(integers(5, 10**4))
    def test_prime_number(self, n):
        assume(FactoringTest.is_prime(n))
        sym_x, sym_y, variable, clauses = factoring_to_sat(n)

        cnf = FactoringTest.cnf_to_pysat(clauses)
        solver = Glucose3(bootstrap_with=cnf)

        assert not solver.solve(), "The formula generated for a prime number should be in UNSAT"

    @staticmethod
    def cnf_to_pysat(clauses):
        formula = CNF()
        formula.from_clauses(clauses)
        return formula

    @staticmethod
    def assignment_to_bin(sym, assignment):
        for s in sym:
            yield bin(assignment[s - 1] > 0)[2:]

    @staticmethod
    def is_prime(number):
        return all(number % i for i in range(2, number))
