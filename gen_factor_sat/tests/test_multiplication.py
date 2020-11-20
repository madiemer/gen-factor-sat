import unittest

from hypothesis import given, assume, settings
from hypothesis.strategies import integers

from gen_factor_sat import strategies
from gen_factor_sat.factoring_sat import create_symbolic_input
from gen_factor_sat.multiplication import karatsuba, wallace_tree


class MultiplierTest(unittest.TestCase):

    @given(integers(0, 2 ** 40), integers(0, 2 ** 40))
    def test_wallace(self, x, y):
        assert MultiplierTest.run_eval(x, y, wallace_tree) == x * y

    @given(integers(0, 2 ** 100), integers(0, 2 ** 100))
    def test_karatsuba(self, x, y):
        assert MultiplierTest.run_eval(x, y, karatsuba) == x * y

    @given(integers(2**70, 2 ** 100), integers(2**20, 2 ** 50))
    def test_split_simplification(self, x, y):
        assume(len(bin(x)[2:]) > 2 * len(bin(y)[2:]))
        assert MultiplierTest.run_eval(x, y, karatsuba) == x * y

    # @given(integers(0, 10 ** 2), integers(0, 10 ** 2))
    # @settings(deadline=2000)
    # def test_tseitin_wallace(self, x, y):
    #     assert MultiplierTest.run_cnf(x, y, wallace_tree) == x * y
    #
    # @given(integers(0, 10 ** 2), integers(0, 10 ** 2))
    # @settings(deadline=2000)
    # def test_tseitin_karatsuba(self, x, y):
    #     assert MultiplierTest.run_cnf(x, y, karatsuba) == x * y

    @staticmethod
    def run_eval(x, y, func):
        bin_x = bin(y)[2:]
        bin_y = bin(x)[2:]

        strategy = strategies.EvalStrategy()
        result = func(bin_x, bin_y, strategy)

        bin_result = ''.join(result)
        return int(bin_result, 2)

    @staticmethod
    def run_cnf(x, y, func):
        bin_x = bin(y)[2:]
        bin_y = bin(x)[2:]

        sym_x, sym_y = create_symbolic_input(len(bin_x), len(bin_y))
        tseitin_strategy = strategies.TseitinStrategy(sym_x + sym_y)

        result = func(sym_x, sym_y, tseitin_strategy)

        variables = tseitin_strategy.variables
        clauses = tseitin_strategy.clauses

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

            if n == len(variables):
                return -1

        result = list(map(lambda x: bin(assignment[x])[2:] if not strategies.is_constant(x) else x, result))
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
        clauses_u = list(filter(lambda clause: u not in clause, clauses))
        clauses_u = list(map(lambda clause: list(filter(lambda l: l != -u, clause)), clauses_u))

        return clauses_u


if __name__ == '__main__':
    unittest.main()
