import re
from collections import Counter

import pytest

from gen_factor_sat import factoring_sat

comment_line = re.compile('c .*')
problem_line = re.compile('p cnf (?P<variables>\\d*) (?P<clauses>\\d*)')
clause_line = re.compile('(-?[1-9][0-9]* )*0')


@pytest.fixture(scope='module', params=[2, 17, 2 ** 15 + 17896, 2 ** 23 + 1247561])
def factoring_instance(request):
    factor_sat = factoring_sat.factorize_number(request.param)
    return factor_sat


def test_dimacs_format(factoring_instance):
    dimacs = factoring_instance.to_dimacs()

    parsed_problem_line = False
    lines = dimacs.splitlines(keepends=False)
    for line in lines:
        if comment_line.match(line):
            assert not parsed_problem_line, 'Comments are only permitted before the problem line'
        elif problem_line.match(line):
            assert not parsed_problem_line, 'The DIMACS format should have exactly one problem line'
            parsed_problem_line = True
        elif clause_line.match(line):
            assert parsed_problem_line, 'Clauses are only permitted after the problem line'
        else:
            assert not line, "Only comment lines, problem lines, or clauses are allowed"

    assert parsed_problem_line, 'The DIMACS format should have exactly one problem line'


def test_encoded_cnf(factoring_instance):
    dimacs = factoring_instance.to_dimacs()

    clauses = []
    lines = dimacs.splitlines(keepends=False)
    for line in lines:
        if problem_line.match(line):
            match = problem_line.match(line)

            num_variables = int(match.group('variables'))
            num_clauses = int(match.group('clauses'))

            assert num_variables == factoring_instance.number_of_variables
            assert num_clauses == len(factoring_instance.clauses)

        elif clause_line.match(line):
            clause = list(map(int, line.split(' ')[:-1]))

            occurrences = Counter(clause)
            assert all(occurrences[-literal] == 0 for literal in clause)
            assert all(occurrences[literal] == 1 for literal in clause)

            clauses.append(frozenset(clause))

    assert len(clauses) == len(factoring_instance.clauses)
    assert set(clauses) == factoring_instance.clauses
