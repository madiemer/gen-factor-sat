import itertools

import pytest

from gen_factor_sat.circuit.tseitin.circuit import CNFBuilder, TseitinGateStrategy
from gen_factor_sat.circuit.tseitin.encoding import and_equality, or_equality, xor_equality, equal_equality
from gen_factor_sat.formula.symbol import constant, variable


@pytest.fixture()
def create_cnf_builder():
    def _create_cnf_builder(initial_variables=None):
        if initial_variables is None:
            cnf_builder = CNFBuilder()
            assert cnf_builder.number_of_variables == 0
        else:
            cnf_builder = CNFBuilder(initial_variables)
            assert cnf_builder.number_of_variables == initial_variables

        return cnf_builder

    return _create_cnf_builder


@pytest.mark.parametrize('initial_variables', [0, 1, 42])
def test_next_variable(create_cnf_builder, initial_variables):
    cnf_builder = create_cnf_builder(initial_variables)

    for i in range(20):
        assert cnf_builder.next_variable() == initial_variables + i + 1, \
            'The variables should be consecutively numbered'

        assert cnf_builder.number_of_variables == initial_variables + i + 1, \
            'The number of variables should be incremented'


@pytest.mark.parametrize('initial_variables', [0, 1, 42])
def test_next_variables(create_cnf_builder, initial_variables):
    cnf_builder = create_cnf_builder(initial_variables)

    expected_variables = list(range(initial_variables + 1, initial_variables + 8))
    assert cnf_builder.next_variables(7) == expected_variables, \
        'The variables should be consecutively numbered'

    assert cnf_builder.number_of_variables == initial_variables + 7, \
        'The number of variables should be incremented'


@pytest.mark.parametrize('initial_variables', [0, 1, 42])
def test_add_clauses(create_cnf_builder, initial_variables):
    variable_1 = variable(15)
    variable_2 = variable(-16)

    cnf_builder = create_cnf_builder(initial_variables)
    tseitin_strategy = TseitinGateStrategy()

    result_and = tseitin_strategy.wire_and(variable_1, variable_2, cnf_builder)
    # The output should be a new variable
    assert cnf_builder.number_of_variables == initial_variables + 1
    assert result_and == initial_variables + 1

    result_or = tseitin_strategy.wire_or(variable_1, variable_2, cnf_builder)
    # The output should be a new variable
    assert cnf_builder.number_of_variables == initial_variables + 2
    assert result_or == initial_variables + 2

    expected_clauses = set()
    expected_clauses.update(and_equality(variable_1, variable_2, result_and))
    expected_clauses.update(or_equality(variable_1, variable_2, result_or))

    assert any(result_and in clause for clause in cnf_builder.clauses), \
        'The value of output should be restricted by the clauses'

    assert any(result_or in clause for clause in cnf_builder.clauses), \
        'The value of output should be restricted by the clauses'

    assert cnf_builder.clauses == expected_clauses, \
        'All clauses should be added to the CNFBuilder'


def test_build_clauses(create_cnf_builder):
    cnf_builder = create_cnf_builder()

    clauses = xor_equality(variable(-1), variable(1), variable(-1))
    cnf_builder.add_clauses(clauses)

    clauses = equal_equality(variable(-1), variable(1), variable(-1))
    cnf_builder.add_clauses(clauses)

    cnf = cnf_builder.build()
    assert not list(filter(has_duplicates, cnf.clauses)), \
        'Build clauses should remove duplicates'


def has_duplicates(clause) -> bool:
    return not isinstance(clause, frozenset) \
           or any(-x in clause for x in clause)


@pytest.mark.parametrize('constant_value', ['0', '1'])
def test_constant_propagation2(constant_value):
    var = variable(1)
    const = constant(constant_value)

    tseitin_strategy = TseitinGateStrategy()
    check_constant_prop(tseitin_strategy.wire_and, args=[var, const], expected=var if const == '1' else '0')
    check_constant_prop(tseitin_strategy.wire_or, args=[var, const], expected=var if const == '0' else '1')
    check_constant_prop(tseitin_strategy.wire_not, args=[const], expected='0' if const == '1' else '1')


def check_constant_prop(method, args, expected):
    cnf_builder = CNFBuilder()
    for combination in itertools.permutations(args):
        result = method(writer=cnf_builder, *combination)

        assert cnf_builder.number_of_variables == 0, \
            'Constant propagation should not create an output variable'

        assert not cnf_builder.clauses, \
            'Constant propagation should not add clauses'

        assert result == expected, \
            'Constant propagation should return the expected result'
