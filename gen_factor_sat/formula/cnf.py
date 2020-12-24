from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set, FrozenSet

from gen_factor_sat.formula.symbol import Variable, variable

Clause = FrozenSet[int]

@dataclass()
class CNF:
    number_of_variables: int
    clauses: Set[Clause]

    def to_dimacs(self: CNF, comments=None) -> str:
        if (comments is None) or (not comments):
            comment_lines = ''
        else:
            prefixed_comments = list(map('c {0}'.format, comments))
            comment_lines = '\n'.join(prefixed_comments) + '\n'

        problem = 'p cnf {0} {1}'.format(self.number_of_variables, len(self.clauses))
        dimacs_clauses = list(map(CNF.clause_to_dimacs, self.clauses))
        cnf_lines = '\n'.join([problem] + dimacs_clauses)

        return comment_lines + cnf_lines

    @staticmethod
    def clause_to_dimacs(clause: Clause) -> str:
        if not clause:
            return '0'
        else:
            return ' '.join(map(str, clause)) + ' 0'


class CNFBuilder:
    def __init__(self, number_of_variables=0):
        self.number_of_variables = number_of_variables
        self.__clauses = set()

    def build(self) -> CNF:
        return CNF(self.number_of_variables, self.build_clauses())

    def build_clauses(self) -> Set[Clause]:
        return set(filter(is_no_tautology, self.__clauses))

    def from_tseitin(self, tseitin_transformation, *args) -> Variable:
        output = self.next_variable()
        clauses = tseitin_transformation(*args, output)
        self.append_clauses(clauses)
        return output

    def next_variables(self, amount: int) -> List[Variable]:
        return [self.next_variable() for _ in range(amount)]

    def next_variable(self) -> Variable:
        self.number_of_variables += 1
        return variable(self.number_of_variables)

    def append_clauses(self, clauses: Set[Clause]):
        self.__clauses.update(clauses)


def is_no_tautology(clause: Clause) -> bool:
    return all(-x not in clause for x in clause)