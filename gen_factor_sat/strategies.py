import operator as op
from typing import Generic, TypeVar, List

from gen_factor_sat import tseitin
from gen_factor_sat.tseitin import Symbol, Constant, Variable, ZERO, ONE

T = TypeVar('T')


class Strategy(Generic[T]):
    def zero(self) -> T:
        pass

    def one(self) -> T:
        pass

    def wire_and(self, x: T, y: T) -> T:
        pass

    def wire_or(self, x: T, y: T) -> T:
        pass

    def wire_xor(self, x: T, y: T) -> T:
        pass

    def wire_not(self, x: T) -> T:
        pass


class EvalStrategy(Strategy[Constant]):

    def zero(self) -> Constant:
        return '0'

    def one(self) -> Constant:
        return '1'

    def wire_and(self, x: Constant, y: Constant) -> Constant:
        return EvalStrategy.__with_bool(op.and_, x, y)

    def wire_or(self, x: Constant, y: Constant) -> Constant:
        return EvalStrategy.__with_bool(op.or_, x, y)

    def wire_xor(self, x: T, y: T) -> T:
        return EvalStrategy.__with_bool(op.xor, x, y)

    def wire_not(self, x: Constant) -> Constant:
        return EvalStrategy.__with_bool(op.not_, x)

    @staticmethod
    def __with_bool(func, *args):
        return EvalStrategy.__to_bin(func(*iter(map(EvalStrategy.__to_bool, args))))

    @staticmethod
    def __to_bool(value: str) -> bool:
        return value == '1'

    @staticmethod
    def __to_bin(value: bool) -> str:
        return bin(value)[2:]


class TseitinStrategy(Strategy[Symbol]):

    def __init__(self, cnf_builder):
        self.cnf_builder = cnf_builder

    def zero(self) -> Constant:
        return '0'

    def one(self) -> Constant:
        return '1'

    def wire_and(self, x: Symbol, y: Symbol) -> Symbol:
        if is_constant(x) or is_constant(y):
            return constant_and(x, y)
        else:
            z = self.cnf_builder.next_variable()
            self.cnf_builder.append_clauses(tseitin.and_equality(x, y, z))
            return z

    def wire_or(self, x: Symbol, y: Symbol) -> Symbol:
        if is_constant(x) or is_constant(y):
            return constant_or(x, y)
        else:
            z = self.cnf_builder.next_variable()
            self.cnf_builder.append_clauses(tseitin.or_equality(x, y, z))
            return z

    def wire_xor(self, x: Symbol, y: Symbol) -> Symbol:
        if is_constant(x) or is_constant(y):
            return constant_xor(x, y)
        else:
            z = self.cnf_builder.next_variable()
            self.cnf_builder.append_clauses(tseitin.xor_equality(x, y, z))
            return z

    def wire_not(self, x: Symbol) -> Symbol:
        if is_constant(x):
            return constant_not(x)
        else:
            return -x

    def assume(self, x: Symbol, value: Constant) -> Constant:
        if is_constant(x) and x != value:
            self.cnf_builder.append_clauses({tseitin.empty_clause()})
        elif not is_constant(x):
            if value == ONE:
                self.cnf_builder.append_clauses({tseitin.unit_clause(x)})
            else:
                self.cnf_builder.append_clauses({tseitin.unit_clause(-x)})

        return value


class CNFBuilder:
    def __init__(self, number_of_variables=0):
        self.number_of_variables = number_of_variables
        self.clauses = set()

    def next_variables(self, amount) -> List[Variable]:
        return [self.next_variable() for _ in range(amount)]

    def next_variable(self) -> Variable:
        self.number_of_variables += 1
        return self.number_of_variables

    def append_clauses(self, clauses):
        self.clauses.update(clauses)


def is_constant(x):
    return x == ZERO or x == ONE


def constant_and(x, y):
    if x == ZERO or y == ZERO:
        return ZERO
    elif x == ONE:
        return y
    elif y == ONE:
        return x


def constant_or(x, y):
    if x == ONE or y == ONE:
        return ONE
    if x == ZERO:
        return y
    elif y == ZERO:
        return x


def constant_xor(x, y):
    if x == ONE:
        if is_constant(y):
            return constant_not(y)
        else:
            return -y
    elif y == ONE:
        if is_constant(x):
            return constant_not(x)
        else:
            return -x
    elif x == ZERO:
        return y
    elif y == ZERO:
        return x
    else:
        raise ValueError()


def constant_not(x):
    if x == ZERO:
        return ONE
    elif x == ONE:
        return ZERO
