from typing import Set, List

from gen_factor_sat.formula.cnf import Clause
from gen_factor_sat.formula.symbol import Variable


def and_equality(input_1: Variable, input_2: Variable, output: Variable) -> Set[Clause]:
    """
    Encode an AND-Gate into a CNF.

    :param input_1: variable representing the first input of the AND-Gate
    :param input_2: variable representing the second input of the AND-Gate
    :param output: variable representing the output of the AND-Gate
    :return: A set of clauses encoding the AND-Gate
    """
    return {
        frozenset([input_1, -output]),
        frozenset([input_2, -output]),
        frozenset([-input_1, -input_2, output])
    }


def or_equality(input_1: Variable, input_2: Variable, output: Variable) -> Set[Clause]:
    """
    Encode an OR-Gate into a CNF.

    :param input_1: variable representing the first input of the OR-Gate
    :param input_2: variable representing the second input of the OR-Gate
    :param output: variable representing the output of the OR-Gate
    :return: A set of clauses encoding the OR-Gate
    """
    return {
        frozenset([-input_1, output]),
        frozenset([-input_2, output]),
        frozenset([input_1, input_2, -output])
    }


def xor_equality(input_1: Variable, input_2: Variable, output: Variable) -> Set[Clause]:
    """
    Encode an XOR-Gate into a CNF.

    :param input_1: variable representing the first input of the XOR-Gate
    :param input_2: variable representing the second input of the XOR-Gate
    :param output: variable representing the output of the XOR-Gate
    :return: A set of clauses encoding the XOR-Gate
    """
    return {
        frozenset([-input_1, -input_2, -output]),
        frozenset([-input_1, input_2, output]),
        frozenset([input_1, -input_2, output]),
        frozenset([input_1, input_2, -output])
    }


def equal_equality(input_1: Variable, input_2: Variable, output: Variable) -> Set[Clause]:
    """
    Encode an Equality-Gate into a CNF.

    :param input_1: variable representing the first input of the Equality-Gate
    :param input_2: variable representing the second input of the Equality-Gate
    :param output: variable representing the output of the Equality-Gate
    :return: A set of clauses encoding the Equality-Gate
    """
    return {
        frozenset([input_1, input_2, output]),
        frozenset([input_1, -input_2, -output]),
        frozenset([-input_1, input_2, -output]),
        frozenset([-input_1, -input_2, output])
    }


def clause(literals: List[Variable]) -> Clause:
    """
    Convert a list of literals into clause representation.

    :param literals: the literals that should be used to create the clause
    :return: the clause consisting of the specified literals
    """
    return frozenset(literals)


def unit_clause(literal: Variable) -> Clause:
    """
    Create a unit clause using the specified literal.

    :param literal: the literal that should be used to create the unit clause
    :return: the resulting unit clause
    """
    return frozenset([literal])


def empty_clause() -> Clause:
    """
    Create an empty clause, which makes formulas unsatisfiable.

    :return: an empty clause
    """
    return frozenset([])
