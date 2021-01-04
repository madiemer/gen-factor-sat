from abc import ABC
from typing import TypeVar, cast

import gen_factor_sat.circuit.tseitin.encoding as te
from gen_factor_sat.circuit.default.circuit import GeneralSimpleCircuitStrategy
from gen_factor_sat.circuit.interface.circuit import GateStrategy
from gen_factor_sat.formula.cnf import CNFBuilder
from gen_factor_sat.formula.symbol import Symbol, Variable, variable, Constant, constant

T = TypeVar('T')


class TseitinGateStrategy(GateStrategy[Symbol, CNFBuilder]):
    zero: Constant = constant('0')
    one: Constant = constant('1')

    def wire_and(self, value_1: Symbol, value_2: Symbol, writer: CNFBuilder) -> Symbol:
        if self.is_constant(value_1) or self.is_constant(value_2):
            return self._constant_and(value_1, value_2)
        else:
            return writer.from_tseitin(te.and_equality, value_1, value_2)

    def wire_or(self, value_1: Symbol, value_2: Symbol, writer: CNFBuilder) -> Symbol:
        if self.is_constant(value_1) or self.is_constant(value_2):
            return self._constant_or(value_1, value_2)
        else:
            return writer.from_tseitin(te.or_equality, value_1, value_2)

    def wire_not(self, value: Symbol, writer: CNFBuilder) -> Symbol:
        if self.is_constant(value):
            return self._constant_not(value)
        else:
            var = cast(Variable, value)  # Type hint
            return variable(-var)

    def expect_zero(self, value: Symbol, writer: CNFBuilder) -> Symbol:
        return self.expect(value, self.zero, writer)

    def expect_one(self, value: Symbol, writer: CNFBuilder) -> Symbol:
        return self.expect(value, self.one, writer)

    def expect(self, symbol: Symbol, value: Constant, writer: CNFBuilder) -> Constant:
        """
        Assume the specified symbol has the expected value. If the evaluation
        of the symbol yields another value the formula will be unsatisfiable.
        As the value of the symbol is now known, the returned symbol is equivalent
        to the specified value.

        :param symbol: the symbol to which the value should be assigned
        :param value: the value that should be assigned to the symbol
        :param writer: the object collecting the written clauses
        :return: the value of the symbol
        """
        if self.is_constant(symbol) and symbol != value:
            writer.add_clauses({te.empty_clause()})
        elif not self.is_constant(symbol):
            var = cast(Variable, symbol)  # Type hint
            if self.is_one(value):
                writer.add_clauses({te.unit_clause(var)})
            else:
                writer.add_clauses({te.unit_clause(variable(-var))})

        return value

    def _constant_and(self, symbol_1: Symbol, symbol_2: Symbol) -> Symbol:
        if symbol_1 == self.zero or symbol_2 == self.zero:
            return self.zero
        elif symbol_1 == self.one:
            return symbol_2
        elif symbol_2 == self.one:
            return symbol_1
        else:
            raise ValueError('Neither {0} nor {1} is a constant'.format(symbol_1, symbol_2))

    def _constant_or(self, symbol_1: Symbol, symbol_2: Symbol) -> Symbol:
        if symbol_1 == self.one or symbol_2 == self.one:
            return self.one
        if symbol_1 == self.zero:
            return symbol_2
        elif symbol_2 == self.zero:
            return symbol_1
        else:
            raise ValueError('Neither {0} nor {1} is a constant'.format(symbol_1, symbol_2))

    def _constant_not(self, symbol: Symbol) -> Symbol:
        if symbol == self.zero:
            return self.one
        elif symbol == self.one:
            return self.zero
        else:
            raise ValueError('{0} is no constant'.format(symbol))


class TseitinCircuitStrategy(GeneralSimpleCircuitStrategy[Symbol, CNFBuilder], ABC):

    def xor(self, value_1: Symbol, value_2: Symbol, writer: CNFBuilder) -> Symbol:
        if self.is_constant(value_1) or self.is_constant(value_2):
            return self._constant_xor(value_1, value_2, writer)
        else:
            return writer.from_tseitin(te.xor_equality, value_1, value_2)

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
