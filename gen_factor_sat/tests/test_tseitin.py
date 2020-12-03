import itertools

import pytest

from gen_factor_sat import tseitin_encoding


@pytest.mark.skip("Currently not supported")
def test_duplicate_variables():
    """Test that the tseitin encoding cannot construct clauses with
    duplicate variables.
    """
    test_values = [241, -31]
    combinations = [(x, y, z) for x in test_values for y in test_values for z in test_values]

    for x, y, z in combinations:
        assert not list(filter(has_duplicates, tseitin_encoding.and_equality(x, y, z)))
        assert not list(filter(has_duplicates, tseitin_encoding.or_equality(x, y, z)))


@pytest.mark.skip("Currently not supported")
def test_tautologies():
    """Test that the tseitin encoding cannot construct tautologies"""
    test_values = [1, -151]
    combinations = list(itertools.product(test_values, repeat=3))

    for x, y, z in combinations:
        for clause in tseitin_encoding.and_equality(x, y, z):
            assert tseitin_encoding.is_no_tautology(clause)

        for clause in tseitin_encoding.or_equality(x, y, z):
            assert tseitin_encoding.is_no_tautology(clause)


def has_duplicates(clause):
    return not isinstance(clause, frozenset) \
           or any(-x in clause for x in clause)


def test_and_encoding():
    variables = [1, 2, 3]

    def and_equality(a, b, c):
        return (a and b) == c

    check_assignments(variables, tseitin_encoding.and_equality(*variables), and_equality)


def test_or_encoding():
    variables = [1, 2, 3]

    def or_equality(a, b, c):
        return (a or b) == c

    check_assignments(variables, tseitin_encoding.or_equality(*variables), or_equality)


def test_xor_encoding():
    variables = [1, 2, 3]

    def xor_equality(a, b, c):
        return (a ^ b) == c

    check_assignments(variables, tseitin_encoding.xor_equality(*variables), xor_equality)


def test_equal_encoding():
    variables = [1, 2, 3]

    def equal_equality(a, b, c):
        return (a == b) == c

    check_assignments(variables, tseitin_encoding.equal_equality(*variables), equal_equality)


def check_assignments(variables, clauses, bool_expr):
    for assignment in itertools.product([False, True], repeat=len(variables)):

        remaining = clauses
        for (x, value) in zip(variables, assignment):
            remaining = assign(x, value, remaining)

        assert not bool(remaining) == bool_expr(*assignment)


def assign(x, value, clauses):
    u = x if value else -x
    clauses_u = list(filter(lambda clause: u not in clause, clauses))
    clauses_u = list(map(lambda clause: list(filter(lambda l: l != -u, clause)), clauses_u))

    return clauses_u
