import unittest

from hypothesis import given
from hypothesis.strategies import integers

from gen_factor_sat import factoring_sat


class DimacsTest(unittest.TestCase):

    @given(integers(2, 2**10))
    def test_duplicate_variables(self, x):
        factor_sat = factoring_sat.factoring_to_sat(x)
        dimacs = factor_sat.to_dimacs()

        assert False, "Not implemented"
