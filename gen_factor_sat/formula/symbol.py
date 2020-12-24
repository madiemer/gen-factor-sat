from typing import NewType, Union

Constant = NewType('Constant', str)
Variable = NewType('Variable', int)
Symbol = Union[Constant, Variable]


def constant(bin_str: str) -> Constant:
    if bin_str == '0' or bin_str == '1':
        return Constant(bin_str)
    else:
        raise ValueError('{0} is no constant'.format(bin_str))


def variable(var_id: int) -> Variable:
    if var_id != 0:
        return Variable(var_id)
    else:
        raise ValueError('0 cannot be used as variable')
