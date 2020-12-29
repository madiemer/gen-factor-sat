from __future__ import annotations

from dataclasses import dataclass
from typing import List, Set, FrozenSet

from gen_factor_sat.formula.symbol import Variable, variable

Clause = FrozenSet[int]


@dataclass()
class CNF:
    """Represents a CNF formula"""
    number_of_variables: int
    clauses: Set[Clause]

    def to_dimacs(self: CNF, comments: List[str] = None) -> str:
        """
        Encode this CNF into the DIMACS format. The specified comment lines
        are included at the beginning. The comments must not contain line
        breaks.

        :param comments: additional information that should be included
        :return: the DIMACS representation of this cnf
        """
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
        """
        Convert the clause into the DIMACS format.

        :param clause: the clause to be encoded
        :return: the DIMACS representation of the clause
        """
        if not clause:
            return '0'
        else:
            return ' '.join(map(str, clause)) + ' 0'


class CNFBuilder:
    """Helper class to construct a CNF formula"""

    def __init__(self, number_of_variables=0):
        self.number_of_variables = number_of_variables
        self.clauses = set()

    def build(self) -> CNF:
        """
        Convert the aggregated clauses into a CNF formula.
        This removes duplicate clauses and clauses that are tautologies.

        :return: the CNF formula
        """
        return CNF(self.number_of_variables, self.build_clauses())

    def build_clauses(self) -> Set[Clause]:
        """
        Remove duplicate clauses and tautologies.

        :return: the filtered clauses
        """
        return set(filter(is_no_tautology, self.clauses))

    def from_tseitin(self, tseitin_transformation, *args) -> Variable:
        output = self.next_variable()
        clauses = tseitin_transformation(*args, output)
        self.add_clauses(clauses)
        return output

    def next_variables(self, amount: int) -> List[Variable]:
        """
        Allocate the specified amount of unused variables. To avoid having
        the same representation for different variables, the variables of
        multiple CNFBuilder must not be mixed.

        :param amount: the amount of variables to be allocated
        :return: the list of the allocated variables
        """
        return [self.next_variable() for _ in range(amount)]

    def next_variable(self) -> Variable:
        """
        Allocate the next unused variable. To avoid having the same representation
        for different variables, the variables of multiple CNFBuilder must not be
        mixed.

        :return: the allocated variable
        """
        self.number_of_variables += 1
        return variable(self.number_of_variables)

    def add_clauses(self, clauses: Set[Clause]) -> None:
        """
        Add the specified clauses to the set of clauses that will be considered when
        building a CNF.

        :param clauses: the clauses to be added
        :return: None
        """
        self.clauses.update(clauses)


def is_no_tautology(clause: Clause) -> bool:
    """
    Check whether the clause is a tautology.

    :param clause: the clause to be checked
    :return: true if the clause is a tautology, otherwise false
    """
    return all(-x not in clause for x in clause)
