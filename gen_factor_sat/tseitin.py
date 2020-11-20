from typing import Union, Set, FrozenSet

Constant = str
Variable = int
Symbol = Union[Constant, Variable]

Clause = FrozenSet[Variable]

ZERO: Constant = '0'
ONE: Constant = '1'


def and_equality(x: Variable, y: Variable, z: Variable) -> Set[Clause]:
    """
    Encode an AND-Gate into a CNF.

    :param x: variable representing the first input of the AND-Gate
    :param y: variable representing the second input of the AND-Gate
    :param z: variable representing the output of the AND-Gate
    :return: A set of clauses encoding the AND-Gate
    """
    return {
        frozenset([x, -z]),
        frozenset([y, -z]),
        frozenset([-x, -y, z])
    }


def or_equality(x: Variable, y: Variable, z: Variable) -> Set[Clause]:
    """
    Encode an OR-Gate into a CNF.

    :param x: variable representing the first input of the OR-Gate
    :param y: variable representing the second input of the OR-Gate
    :param z: variable representing the output of the AND-Gate
    :return: A set of clauses encoding the OR-Gate
    """
    return {
        frozenset([-x, y, z]),
        frozenset([x, -y, z]),
        frozenset([x, y, -z])
    }


def empty_clause(x: Variable) -> Set[Clause]:
    return {frozenset([x]), frozenset([-x])}


def is_no_tautology(clause: Clause) -> bool:
    return clause and all(-x not in clause for x in clause)
