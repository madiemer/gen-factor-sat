import unittest

from hypothesis import given, assume
from hypothesis.strategies import integers

import SATGenerator

import Tseitin


class DimacsTest(unittest.TestCase):

    @given(integers(2, 2**10))
    def test_duplicate_variables(self, x):
        variables, clauses = SATGenerator.factoring_to_sat(x)
        dimacs = SATGenerator.result_to_dimacs(variables, clauses)

        assert False, "Not implemented"
