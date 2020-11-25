import re

from hypothesis import given
from hypothesis.strategies import integers

from gen_factor_sat import factoring_sat
from gen_factor_sat import tseitin

comment_line = re.compile('c .*')
problem_line = re.compile('p cnf (?P<variables>\\d*) (?P<clauses>\\d*)')
clause_line = re.compile('(-?[1-9][0-9]* )*0')


@given(integers(2, 2 ** 10))
def test_duplicate_variables(x):
    factor_sat = factoring_sat.factorize_number(x)
    dimacs = factor_sat.to_dimacs()

    clauses = []
    variables = set()
    p_line = False

    lines = dimacs.splitlines(keepends=False)
    for line in lines:
        if comment_line.match(line):
            assert not p_line, 'Comments are permitted before the problem line'
        elif problem_line.match(line):
            assert not p_line, 'Only a single problem line is permitted'
            p_line = True

            m = problem_line.match(line)
            num_vars = int(m.group('variables'))
            num_clauses = int(m.group('clauses'))

        elif clause_line.match(line):
            assert problem_line, 'Clauses are permitted only after the problem line'

            clause = list(map(int, line.split(' ')[:-1]))
            variables.update(set(map(abs, clause)))
            clauses.append(clause)
        else:
            assert not line, "Not a valid line: " + line

    assert not list(filter(lambda x: not tseitin.is_no_tautology(x), clauses))
    assert p_line, 'There should be a cnf problem encoded'
    assert len(variables) == num_vars, 'Every variable should occur at least once'
    assert all(x <= num_vars for x in variables), 'Variables should be numbered from 1 to the specified number'
    assert len(clauses) == num_clauses, 'The number of clauses should match the specified number'
