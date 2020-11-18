from typing import Union, Set, FrozenSet

from gen_factor_sat.circuit import Constant

Variable = int
Symbol = Union[Constant, Variable]

Clause = FrozenSet[Symbol]


def equality(x: Symbol, y: Symbol) -> Set[Clause]:
    clauses = map(simplify_constant, {
        frozenset([not_symbol(x), y]),
        frozenset([x, not_symbol(y)])
    })

    return set(filter(is_no_tautology, clauses))


def and_equality(x: Variable, y: Variable, z: Variable) -> Set[Clause]:
    clauses = map(simplify_constant, {
        frozenset([x, not_symbol(z)]),
        frozenset([y, not_symbol(z)]),
        frozenset([not_symbol(x), not_symbol(y), z])
    })

    return set(filter(is_no_tautology, clauses))


def or_equality(x: Variable, y: Variable, z: Variable) -> Set[Clause]:
    clauses = map(simplify_constant, {
        frozenset([not_symbol(x), y, z]),
        frozenset([x, not_symbol(y), z]),
        frozenset([x, y, not_symbol(z)])
    })

    return set(filter(is_no_tautology, clauses))


def not_symbol(x: Symbol) -> Symbol:
    if isinstance(x, Constant):
        return not_constant(x)
    elif isinstance(x, Variable):
        return -x


def not_constant(x: Constant) -> Constant:
    if x == '1':
        return '0'
    elif x == '0':
        return '1'
    else:
        raise ValueError("{0} is no constant".format(x))


def simplify_constant(clause: Clause) -> Clause:
    if '1' in clause:
        # Clause is a tautology
        return frozenset([])
    else:
        # Remove false literals
        return frozenset([x for x in clause if x != '0'])


def is_no_tautology(clause: Clause) -> bool:
    return clause and all(-x not in clause for x in clause)
