import unittest

from hypothesis import given, settings, assume
from hypothesis.strategies import integers
from pysat.formula import CNF
from pysat.solvers import Cadical
from random import Random
from gen_factor_sat.factoring_sat import factoring_to_sat, generate_factoring_to_sat, _generate_number


class FactoringTest(unittest.TestCase):

    def test_reproducibility(self):
        factoring_1 = generate_factoring_to_sat(213198414)
        factoring_2 = generate_factoring_to_sat(213198414)

        self.assertNotEqual(factoring_1, factoring_2)

    @given(integers(2, 2 ** 40), integers(2, 2 ** 40))
    @settings(deadline=None, max_examples=10)
    def test_composite_number(self, x, y):
        factor_sat = factoring_to_sat(x * y)

        formula = CNF()
        formula.from_clauses(factor_sat.clauses)
        solver = Cadical(bootstrap_with=formula)

        self.assertTrue(solver.solve(), "The formula generated for a composite number should be in SAT")

        result_a = int(''.join(FactoringTest.assignment_to_bin(factor_sat.factor_1, solver.get_model())), 2)
        result_b = int(''.join(FactoringTest.assignment_to_bin(factor_sat.factor_2, solver.get_model())), 2)

        print(len(bin(x * y)) > 2 ** 40)
        self.assertEqual(result_a * result_b, x * y, "Result a and b should contain all factors of x and y")

    @given(integers(2, 2 ** 50))
    @settings(deadline=None, max_examples=20)
    def test_prime_number(self, n):
        assume(FactoringTest.primt(n))
        factor_sat = factoring_to_sat(n)

        formula = CNF()
        formula.from_clauses(factor_sat.clauses)
        solver = Cadical(bootstrap_with=formula)

        print("Test")
        self.assertFalse(solver.solve(), "The formula generated for a prime number should be in UNSAT")

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
