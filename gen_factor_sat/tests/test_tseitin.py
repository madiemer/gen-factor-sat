import unittest

from hypothesis import given, assume
from hypothesis.strategies import integers

from gen_factor_sat import tseitin


class TseitinTest(unittest.TestCase):

    @given(integers())
    def test_duplicate_variables(self, x):
        assume(x != 0)
        clauses = tseitin.equality(x, x)

        for clause in clauses:
            assert type(clause) is frozenset
            assert all(-x not in clause for x in clause)

        clauses = tseitin.equality(x, -x)

        for clause in clauses:
            assert type(clause) is frozenset
            assert all(-x not in clause for x in clause)
