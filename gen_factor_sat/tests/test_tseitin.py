import unittest

from gen_factor_sat import tseitin


class TseitinTest(unittest.TestCase):

    def test_duplicate_variables(self):
        """Test that the tseitin encoding cannot construct clauses with
        duplicate variables.
        """
        test_values = [241, -31]
        combinations = [(x, y, z) for x in test_values for y in test_values for z in test_values]

        for x, y, z in combinations:
            assert not list(filter(TseitinTest.has_duplicates, tseitin.and_equality(x, y, z)))
            assert not list(filter(TseitinTest.has_duplicates, tseitin.or_equality(x, y, z)))

    def test_tautologies(self):
        """Test that the tseitin encoding cannot construct tautologies"""
        test_values = [1, -151]
        combinations = [(x, y, z) for x in test_values for y in test_values for z in test_values]

        for x, y, z in combinations:
            assert all(clause for clause in tseitin.and_equality(x, y, z))
            assert all(clause for clause in tseitin.or_equality(x, y, z))

    @staticmethod
    def has_duplicates(clause):
        return not isinstance(clause, frozenset) \
               or any(-x in clause for x in clause)
