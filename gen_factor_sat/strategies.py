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

    def wire_not(self, x: T) -> T:
        pass


class EvalStrategy(Strategy[Constant]):

    def zero(self) -> Constant:
        return '0'

    def one(self) -> Constant:
        return '1'

    def wire_and(self, x: Constant, y: Constant) -> Constant:
        return bin((x == '1') and (y == '1'))[2:]

    def wire_or(self, x: Constant, y: Constant) -> Constant:
        return bin((x == '1') or (y == '1'))[2:]

    def wire_not(self, x: Constant) -> Constant:
        return bin(not (x == '1'))[2:]


class TseitinStrategy(Strategy[Symbol]):

    def __init__(self, number_of_variables=0):
        self.number_of_variables = number_of_variables
        self.clauses = set()

    def zero(self) -> Constant:
        return '0'

    def one(self) -> Constant:
        return '1'

    def wire_and(self, x: Symbol, y: Symbol) -> Symbol:
        if is_constant(x) or is_constant(y):
            return constant_and(x, y)
        else:
            z = self.next_variable()
            self.clauses.update(tseitin.and_equality(x, y, z))
            return z

    def wire_or(self, x: Symbol, y: Symbol) -> Symbol:
        if is_constant(x) or is_constant(y):
            return constant_or(x, y)
        else:
            z = self.next_variable()
            self.clauses.update(tseitin.or_equality(x, y, z))
            return z

    def wire_not(self, x: Symbol) -> Symbol:
        if is_constant(x):
            return constant_not(x)
        else:
            return -x

    def assume(self, x: Symbol, value: Constant) -> Constant:
        if is_constant(x) and x != value:
            self.clauses.add(tseitin.empty_clause())
        elif not is_constant(x):
            if value == ONE:
                self.clauses.add(tseitin.unit_clause(x))
            else:
                self.clauses.add(tseitin.unit_clause(-x))

        return value

    def next_variables(self, amount) -> List[Variable]:
        return [self.next_variable() for _ in range(amount)]

    def next_variable(self) -> Variable:
        self.number_of_variables += 1
        return self.number_of_variables


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
    elif x == ZERO:
        return y
    elif y == ZERO:
        return x


def constant_not(x):
    if x == ZERO:
        return ONE
    elif x == ONE:
        return ZERO
