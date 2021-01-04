"""
Symbol

Types to represent a symbolic evaluation.
"""

from typing import NewType, Union

Constant = NewType('Constant', str)
Variable = NewType('Variable', int)
Symbol = Union[Constant, Variable]


def constant(bin_str: str) -> Constant:
    """
    Transform the given binary value into a typesafe Constant.
    Ensures that the input string is '0' or '1'.

    :param bin_str: the binary string to be converted
    :return: the Constant
    :raises ValueError if the input is no binary value
    """
    if bin_str in ('0', '1'):
        return Constant(bin_str)
    else:
        raise ValueError('{0} is no constant'.format(bin_str))


def variable(var_id: int) -> Variable:
    """
    Transform the given id into a typesafe Variable.
    Ensures that the input is not 0.

    :param var_id: the variable id to be converted
    :return: the Variable
    :raises ValueError if the input is not a valid id
    """
    if var_id != 0:
        return Variable(var_id)
    else:
        raise ValueError('0 cannot be used as variable')
