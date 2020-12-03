from typing import List, TypeVar

from gen_factor_sat import tseitin_encoding
from gen_factor_sat.circuit import GateStrategy, GeneralCircuitStrategy
from gen_factor_sat.tseitin_encoding import Symbol, Constant, Variable, constant, variable

T = TypeVar('T')


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
        return variable(self.number_of_variables)

    def append_clauses(self, clauses):
        self.clauses.update(clauses)


class TseitinStrategy(GateStrategy[Symbol]):
    zero: Constant = constant('0')
    one: Constant = constant('1')

    def __init__(self, cnf_builder: CNFBuilder):
        self.cnf_builder = cnf_builder

    def wire_and(self, x: Symbol, y: Symbol) -> Symbol:
        if self.is_constant(x) or self.is_constant(y):
            return self._constant_and(x, y)
        else:
            return self.cnf_builder.from_tseitin(tseitin_encoding.and_equality, x, y)

    def wire_or(self, x: Symbol, y: Symbol) -> Symbol:
        if self.is_constant(x) or self.is_constant(y):
            return self._constant_or(x, y)
        else:
            return self.cnf_builder.from_tseitin(tseitin_encoding.or_equality, x, y)

    def wire_not(self, x: Symbol) -> Symbol:
        if self.is_constant(x):
            return self._constant_not(x)
        else:
            return variable(-x)

    def _constant_and(self, x, y):
        if x == self.zero or y == self.zero:
            return self.zero
        elif x == self.one:
            return y
        elif y == self.one:
            return x
        else:
            raise ValueError('Neither {0} nor {1} is a constant'.format(x, y))

    def _constant_or(self, x, y):
        if x == self.one or y == self.one:
            return self.one
        if x == self.zero:
            return y
        elif y == self.zero:
            return x
        else:
            raise ValueError('Neither {0} nor {1} is a constant'.format(x, y))

    def _constant_not(self, x):
        if x == self.zero:
            return self.one
        elif x == self.one:
            return self.zero
        else:
            raise ValueError('{0} is no constant'.format(x))


class TseitinCircuitStrategy(GeneralCircuitStrategy[Symbol]):

    def __init__(self, cnf_builder: CNFBuilder, gate_strategy: GateStrategy[Symbol]):
        super(TseitinCircuitStrategy, self).__init__(gate_strategy=gate_strategy)
        self.cnf_builder = cnf_builder

    def xor(self, x: Symbol, y: Symbol) -> Symbol:
        if self.gate_strategy.is_constant(x) or self.gate_strategy.is_constant(y):
            return self._constant_xor(x, y)
        else:
            return self.cnf_builder.from_tseitin(tseitin_encoding.xor_equality, x, y)

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
        if self.gate_strategy.is_constant(x) and x != value:
            self.cnf_builder.append_clauses({tseitin_encoding.empty_clause()})
        elif not self.gate_strategy.is_constant(x):
            if value == self.gate_strategy.one:
                self.cnf_builder.append_clauses({tseitin_encoding.unit_clause(x)})
            else:
                self.cnf_builder.append_clauses({tseitin_encoding.unit_clause(variable(-x))})

        return value

    def _constant_xor(self, x, y):
        if x == self.gate_strategy.one:
            return self.gate_strategy.wire_not(y)
        elif y == self.gate_strategy.one:
            return self.gate_strategy.wire_not(x)
        elif x == self.gate_strategy.zero:
            return y
        elif y == self.gate_strategy.zero:
            return x
        else:
            raise ValueError('Neither {0} nor {1} is a constant'.format(x, y))

