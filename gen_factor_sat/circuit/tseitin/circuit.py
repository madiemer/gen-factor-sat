from abc import ABC
from typing import List, TypeVar, Set, cast

import gen_factor_sat.circuit.tseitin.encoding as te
from gen_factor_sat.circuit.default.circuit import Constant, constant, GeneralSimpleCircuitStrategy
from gen_factor_sat.circuit.interface.circuit import GateStrategy
from gen_factor_sat.circuit.tseitin.encoding import Symbol, Variable, variable, Clause

T = TypeVar('T')


class CNFBuilder:
    def __init__(self, number_of_variables=0):
        self.number_of_variables = number_of_variables
        self.__clauses = set()

    def build_clauses(self) -> Set[Clause]:
        return set(filter(te.is_no_tautology, self.__clauses))

    def from_tseitin(self, tseitin_transformation, *args) -> Variable:
        output = self.next_variable()
        clauses = tseitin_transformation(*args, output)
        self.append_clauses(clauses)
        return output

    def next_variables(self, amount: int) -> List[Variable]:
        return [self.next_variable() for _ in range(amount)]

    def next_variable(self) -> Variable:
        self.number_of_variables += 1
        return variable(self.number_of_variables)

    def append_clauses(self, clauses: Set[Clause]):
        self.__clauses.update(clauses)


class TseitinGateStrategy(GateStrategy[Symbol, CNFBuilder]):
    zero: Constant = constant('0')
    one: Constant = constant('1')

    def assume(self, symbol: Symbol, value: Constant, writer: CNFBuilder) -> Constant:
        if self.is_constant(symbol) and symbol != value:
            writer.append_clauses({te.empty_clause()})
        elif not self.is_constant(symbol):
            var = cast(Variable, symbol)  # Type hint
            if value == self.one:
                writer.append_clauses({te.unit_clause(var)})
            else:
                writer.append_clauses({te.unit_clause(variable(-var))})

        return value

    def wire_and(self, input_1: Symbol, input_2: Symbol, writer: CNFBuilder) -> Symbol:
        if self.is_constant(input_1) or self.is_constant(input_2):
            return self._constant_and(input_1, input_2)
        else:
            return writer.from_tseitin(te.and_equality, input_1, input_2)

    def wire_or(self, input_1: Symbol, input_2: Symbol, writer: CNFBuilder) -> Symbol:
        if self.is_constant(input_1) or self.is_constant(input_2):
            return self._constant_or(input_1, input_2)
        else:
            return writer.from_tseitin(te.or_equality, input_1, input_2)

    def wire_not(self, input: Symbol, writer: CNFBuilder) -> Symbol:
        if self.is_constant(input):
            return self._constant_not(input)
        else:
            var = cast(Variable, input)  # Type hint
            return variable(-var)

    def _constant_and(self, input_1, input_2):
        if input_1 == self.zero or input_2 == self.zero:
            return self.zero
        elif input_1 == self.one:
            return input_2
        elif input_2 == self.one:
            return input_1
        else:
            raise ValueError('Neither {0} nor {1} is a constant'.format(input_1, input_2))

    def _constant_or(self, input_1, input_2):
        if input_1 == self.one or input_2 == self.one:
            return self.one
        if input_1 == self.zero:
            return input_2
        elif input_2 == self.zero:
            return input_1
        else:
            raise ValueError('Neither {0} nor {1} is a constant'.format(input_1, input_2))

    def _constant_not(self, x):
        if x == self.zero:
            return self.one
        elif x == self.one:
            return self.zero
        else:
            raise ValueError('{0} is no constant'.format(x))


class TseitinCircuitStrategy(GeneralSimpleCircuitStrategy[Symbol, CNFBuilder], ABC):

    def xor(self, input_1: Symbol, input_2: Symbol, writer: CNFBuilder) -> Symbol:
        if self.is_constant(input_1) or self.is_constant(input_2):
            return self._constant_xor(input_1, input_2, writer)
        else:
            return writer.from_tseitin(te.xor_equality, input_1, input_2)

    # def equality(self, x: Symbol, y: Symbol) -> Symbol:
    #     if _is_constant(x):
    #         return self.assume(y, x)
    #     elif _is_constant(y):
    #         return self.assume(x, y)
    #     else:
    #         z = self.gate_builder.cnf_builder.next_variable()
    #         self.gate_builder.cnf_builder.append_clauses(tseitin.equal_equality(x, y, z))
    #         return z

    def _constant_xor(self, input_1, input_2, writer: CNFBuilder):
        if input_1 == self.one:
            return self.wire_not(input_2, writer)
        elif input_2 == self.one:
            return self.wire_not(input_1, writer)
        elif input_1 == self.zero:
            return input_2
        elif input_2 == self.zero:
            return input_1
        else:
            raise ValueError('Neither {0} nor {1} is a constant'.format(input_1, input_2))
