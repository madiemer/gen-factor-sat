from typing import Union, Set, FrozenSet

Constant = str
Variable = int
Symbol = Union[Constant, Variable]

Clause = FrozenSet[Symbol]

ZERO: Constant = '0'
ONE: Constant = '1'


def and_equality(x: Variable, y: Variable, z: Variable) -> Set[Clause]:
    clauses = {
        frozenset([x, -z]),
        frozenset([y, -z]),
        frozenset([-x, -y, z])
    }

    return set(filter(is_no_tautology, clauses))


def or_equality(x: Variable, y: Variable, z: Variable) -> Set[Clause]:
    clauses = {
        frozenset([-x, y, z]),
        frozenset([x, -y, z]),
        frozenset([x, y, -z])
    }

    return set(filter(is_no_tautology, clauses))


def empty_clause(x: Variable) -> Set[Clause]:
    return {frozenset([x]), frozenset([-x])}


def is_no_tautology(clause: Clause) -> bool:
    return clause and all(-x not in clause for x in clause)
