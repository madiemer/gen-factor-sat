import operator as op
from typing import List

from gen_factor_sat import tseitin
from gen_factor_sat.circuit import GateStrategy, CircuitStrategy
from gen_factor_sat.tseitin import Symbol, Constant, Variable, ZERO, ONE


class BooleanStrategy(GateStrategy[Constant]):

    def zero(self) -> Constant:
        return '0'

    def one(self) -> Constant:
        return '1'

    def wire_and(self, x: Constant, y: Constant) -> Constant:
        return BooleanStrategy.__with_bool(op.and_, x, y)

    def wire_or(self, x: Constant, y: Constant) -> Constant:
        return BooleanStrategy.__with_bool(op.or_, x, y)

    def wire_not(self, x: Constant) -> Constant:
        return BooleanStrategy.__with_bool(op.not_, x)

    @staticmethod
    def __with_bool(func, *args):
        return BooleanStrategy.__to_bin(func(*iter(map(BooleanStrategy.__to_bool, args))))

    @staticmethod
    def __to_bool(value: str) -> bool:
        return value == '1'

    @staticmethod
    def __to_bin(value: bool) -> str:
        return bin(value)[2:]


class TseitinStrategy(GateStrategy[Symbol]):

    def __init__(self, cnf_builder):
        self.cnf_builder = cnf_builder

    def zero(self) -> Constant:
        return '0'

    def one(self) -> Constant:
        return '1'

    def wire_and(self, x: Symbol, y: Symbol) -> Symbol:
        if _is_constant(x) or _is_constant(y):
            return _constant_and(x, y)
        else:
            z = self.cnf_builder.next_variable()
            self.cnf_builder.append_clauses(tseitin.and_equality(x, y, z))
            return z

    def wire_or(self, x: Symbol, y: Symbol) -> Symbol:
        if _is_constant(x) or _is_constant(y):
            return _constant_or(x, y)
        else:
            z = self.cnf_builder.next_variable()
            self.cnf_builder.append_clauses(tseitin.or_equality(x, y, z))
            return z

    def wire_not(self, x: Symbol) -> Symbol:
        if _is_constant(x):
            return _constant_not(x)
        else:
            return -x


class TseitinCircuitStrategy(CircuitStrategy[Symbol]):
    def __init__(self, cnf_builder, gate_strategy):
        super(TseitinCircuitStrategy, self).__init__(gate_strategy=gate_strategy)
        self.cnf_builder = cnf_builder

    def xor(self, x: Symbol, y: Symbol) -> Symbol:
        if _is_constant(x) or _is_constant(y):
            return _constant_xor(x, y)
        else:
            z = self.cnf_builder.next_variable()
            self.cnf_builder.append_clauses(tseitin.xor_equality(x, y, z))
            return z

    # def equality(self, x: Symbol, y: Symbol) -> Symbol:
    #     if _is_constant(x):
    #         return self.assume(y, x)
    #     elif _is_constant(y):
    #         return self.assume(x, y)
    #     else:
    #         z = self.gate_builder.cnf_builder.next_variable()
    #         self.gate_builder.cnf_builder.append_clauses(tseitin.equal_equality(x, y, z))
    #         return z

    def assume(self, x: Symbol, value: Constant) -> Constant:
        if _is_constant(x) and x != value:
            self.cnf_builder.append_clauses({tseitin.empty_clause()})
        elif not _is_constant(x):
            if value == ONE:
                self.cnf_builder.append_clauses({tseitin.unit_clause(x)})
            else:
                self.cnf_builder.append_clauses({tseitin.unit_clause(-x)})

        return value


class CNFBuilder:
    def __init__(self, number_of_variables=0):
        self.number_of_variables = number_of_variables
        self.clauses = set()

    def from_tseitin(self, tseitin_transformation, *args):
        z = self.next_variable()
        clauses = tseitin_transformation(*args, z)
        self.append_clauses(clauses)
        return z

    def next_variables(self, amount) -> List[Variable]:
        return [self.next_variable() for _ in range(amount)]

    def next_variable(self) -> Variable:
        self.number_of_variables += 1
        return self.number_of_variables

    def append_clauses(self, clauses):
        self.clauses.update(clauses)


def _is_constant(x):
    return x == ZERO or x == ONE


def _constant_and(x, y):
    if x == ZERO or y == ZERO:
        return ZERO
    elif x == ONE:
        return y
    elif y == ONE:
        return x


def _constant_or(x, y):
    if x == ONE or y == ONE:
        return ONE
    if x == ZERO:
        return y
    elif y == ZERO:
        return x


def _constant_xor(x, y):
    if x == ONE:
        if _is_constant(y):
            return _constant_not(y)
        else:
            return -y
    elif y == ONE:
        if _is_constant(x):
            return _constant_not(x)
        else:
            return -x
    elif x == ZERO:
        return y
    elif y == ZERO:
        return x
    else:
        raise ValueError()


def _constant_not(x):
    if x == ZERO:
        return ONE
    elif x == ONE:
        return ZERO
