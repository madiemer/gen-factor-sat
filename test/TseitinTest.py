import unittest

from hypothesis import given, assume
from hypothesis.strategies import integers

from SATGenerator import factoring_to_sat

import Tseitin

class TseitinTest(unittest.TestCase):

    @given(integers())
    def test_duplicate_variables(self, x):
        assume(x != 0)
        clauses = Tseitin.equality(x, x)

        for clause in clauses:
            assert type(clause) is frozenset
            assert all(-x not in clause for x in clause)

        clauses = Tseitin.equality(x, -x)

        for clause in clauses:
            assert type(clause) is frozenset
            assert all(-x not in clause for x in clause)

