import re
import unittest

from hypothesis import given
from hypothesis.strategies import integers

from gen_factor_sat import factoring_sat
from gen_factor_sat import tseitin

class DimacsTest(unittest.TestCase):
    comment_line = re.compile('c .*')
    problem_line = re.compile('p (?P<variables>\\d*) (?P<clauses>\\d*)')
    clause_line = re.compile('(-?[1-9][0-9]* )+0')

    @given(integers(2, 2 ** 50))
    def test_duplicate_variables(self, x):
        factor_sat = factoring_sat.factoring_to_sat(x)
        dimacs = factor_sat.to_dimacs()

        clauses = []
        variables = set()
        problem_line = False

        lines = dimacs.splitlines(keepends=False)
        for line in lines:
            if self.comment_line.match(line):
                self.assertFalse(problem_line, 'Comments are permitted before the problem line')
            elif self.problem_line.match(line):
                self.assertFalse(problem_line, 'Only a single problem line is permitted')
                problem_line = True

                m = self.problem_line.match(line)
                num_vars = int(m.group('variables'))
                num_clauses = int(m.group('clauses'))

            elif self.clause_line.match(line):
                self.assertTrue(problem_line, 'Clauses are permitted only after the problem line')

                clause = list(map(int, line.split(' ')[:-1]))
                variables.update(set(map(abs, clause)))
                clauses.append(clause)
            else:
                assert not line, "Not a valid line: " + line

        self.assertFalse(list(filter(lambda x: not tseitin.is_no_tautology(x), clauses)))
        self.assertTrue(problem_line, 'There should be a cnf problem encoded')
        self.assertEqual(len(variables), num_vars, 'Every variable should occur at least once')
        self.assertTrue(all(x <= num_vars for x in variables), 'Variables should be numbered from 1 to the specified number')
        self.assertEqual(len(clauses), num_clauses, 'The number of clauses should match the specified number')
