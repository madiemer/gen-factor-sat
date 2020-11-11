import unittest

from hypothesis import given
from hypothesis.strategies import integers

import Strategy
from Karatsuba import karatsuba
from WallaceTree import wallace_tree


class MultiplierTest(unittest.TestCase):

    @given(integers(0, 10 ** 20), integers(0, 10 ** 20))
    def test_wallace(self, x, y):
        assert MultiplierTest.run_eval(x, y, wallace_tree) == x * y

    @given(integers(0, 10 ** 20), integers(0, 10 ** 20))
    def test_karatsuba(self, x, y):
        assert MultiplierTest.run_eval(x, y, karatsuba) == x * y

    @given(integers(0, 10 ** 2), integers(0, 10 ** 2))
    def test_tseitin_wallace(self, x, y):
        assert MultiplierTest.run_tseitin(x, y, wallace_tree) == x * y

    @given(integers(0, 10 ** 2), integers(0, 10 ** 2))
    def test_tseitin_karatsuba(self, x, y):
        assert MultiplierTest.run_tseitin(x, y, karatsuba) == x * y

    @staticmethod
    def run_eval(x, y, func):
        bin_x = bin(y)[2:]
        bin_y = bin(x)[2:]

        strategy = Strategy.EvalStrategy()
        result = func(bin_x, bin_y, strategy)

        bin_result = ''.join(result)
        return int(bin_result, 2)

    @staticmethod
    def run_tseitin(x, y, func):
        bin_x = bin(y)[2:]
        bin_y = bin(x)[2:]

        # Variable 0 cannot be negated
        sym_x = list(range(1, len(bin_x) + 1))
        sym_y = list(range(len(bin_x) + 1, len(bin_x) + len(bin_y) + 1))

        strategy = Strategy.TseitinStrategy(sym_x + sym_y)
        result = func(sym_x, sym_y, strategy)

        clauses = strategy.clauses
        assignment = {}
        for x, a in zip(sym_x, bin_x):
            clauses = MultiplierTest.assign(x, a == '1', clauses)
            assignment[x] = a == '1'

        for y, a in zip(sym_y, bin_y):
            clauses = MultiplierTest.assign(y, a == '1', clauses)
            assignment[y] = a == '1'

        n = 0
        while clauses:
            n += 1
            new_assignments, clauses = MultiplierTest.unit_propagation(clauses)
            assignment = {**assignment, **new_assignments}

            if n == len(strategy.variables):
                return -1

        result = list(map(lambda x: bin(assignment[x])[2:] if not Strategy.is_constant(x) else x, result))
        bin_result = ''.join(result)
        return int(bin_result, 2)

    @staticmethod
    def unit_propagation(clauses):
        assignments = {}
        for clause in clauses:
            if len(clause) == 1:
                x, = clause
                assignments[abs(x)] = x >= 0

        for x, a in assignments.items():
            clauses = MultiplierTest.assign(x, a, clauses)

        return assignments, clauses

    @staticmethod
    def assign(x, value, clauses):
        u = x if value else -x
        clauses_u = [clause for clause in clauses if u not in clause]
        clauses_u = [[l for l in clause if l != -u] for clause in clauses_u]

        return clauses_u


if __name__ == '__main__':
    unittest.main()
