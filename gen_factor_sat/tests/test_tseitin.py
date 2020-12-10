import itertools

import pytest

from gen_factor_sat import tseitin_encoding


@pytest.mark.parametrize('variables', [[1, 2, 3]])
@pytest.mark.parametrize('tseitin, bool_expr', [
    (tseitin_encoding.and_equality, lambda x, y, z: (x and y) == z),
    (tseitin_encoding.or_equality, lambda x, y, z: (x or y) == z),
    (tseitin_encoding.xor_equality, lambda x, y, z: (x ^ y) == z),
    (tseitin_encoding.equal_equality, lambda x, y, z: (x == y) == z)
])
def test_clause_assignments(variables, tseitin, bool_expr):
    check_assignments(variables, tseitin(*variables), bool_expr)


def check_assignments(variables, clauses, bool_expr):
    for assignment in itertools.product([False, True], repeat=len(variables)):

        remaining = clauses
        for (variable, value) in zip(variables, assignment):
            remaining = assign(variable, value, remaining)

        assert not bool(remaining) == bool_expr(*assignment)


def assign(x, value, clauses):
    u = x if value else -x
    clauses_u = list(filter(lambda clause: u not in clause, clauses))
    clauses_u = list(map(lambda clause: list(filter(lambda l: l != -u, clause)), clauses_u))

    return clauses_u
