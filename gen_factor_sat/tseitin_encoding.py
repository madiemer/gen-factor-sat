from typing import Union, Set, FrozenSet, List, NewType

Constant = NewType('Constant', str)
Variable = NewType('Variable', int)
Symbol = Union[Constant, Variable]

Clause = FrozenSet[Variable]


def constant(x: str) -> Constant:
    if x == '0' or x == '1':
        return Constant(x)
    else:
        raise ValueError('{0} is no constant'.format(x))


def variable(x: int) -> Variable:
    if x != 0:
        return Variable(x)
    else:
        raise ValueError('0 cannot be used as variable')


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
    return frozenset(literals)


def unit_clause(literal: Variable) -> Clause:
    return frozenset([literal])


def empty_clause() -> Clause:
    return frozenset([])


def is_no_tautology(clause: Clause) -> bool:
    return all(-x not in clause for x in clause)
