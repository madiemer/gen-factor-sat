import itertools

import pytest

import gen_factor_sat.circuit.tseitin.encoding as te
import gen_factor_sat.tests.utils as test_utils


@pytest.mark.parametrize('variables', [[1, 2, 3]])
@pytest.mark.parametrize('tseitin, bool_expr', [
    (te.and_equality, lambda x, y, z: (x and y) == z),
    (te.or_equality, lambda x, y, z: (x or y) == z),
    (te.xor_equality, lambda x, y, z: (x ^ y) == z),
    (te.equal_equality, lambda x, y, z: (x == y) == z)
])
def test_clause_assignments(variables, tseitin, bool_expr):
    check_assignments(variables, tseitin(*variables), bool_expr)


def check_assignments(variables, clauses, bool_expr):
    for values in itertools.product([False, True], repeat=len(variables)):
        assignment = list(test_utils.assign(variables, values))
        result = test_utils.run_cnf(assignment, [], clauses)

        assert (result is not None) == bool_expr(*values)
