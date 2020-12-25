import pytest

from gen_factor_sat.formula.symbol import constant, variable
from gen_factor_sat.circuit.tseitin.circuit import CNFBuilder, TseitinGateStrategy
from gen_factor_sat.circuit.tseitin.encoding import and_equality, or_equality, xor_equality, equal_equality


@pytest.fixture()
def create_cnf_builder():
    def _create_cnf_builder(initial_variables=0):
        if initial_variables is 0:
            cnf_builder = CNFBuilder()
        else:
            cnf_builder = CNFBuilder(initial_variables)

        assert cnf_builder.number_of_variables == initial_variables
        return cnf_builder

    return _create_cnf_builder


@pytest.mark.parametrize('initial_variables', [0, 1, 42])
def test_next_variable(create_cnf_builder, initial_variables):
    cnf_builder = create_cnf_builder(initial_variables)

    for i in range(20):
        assert cnf_builder.next_variable() == initial_variables + i + 1
        assert cnf_builder.number_of_variables == initial_variables + i + 1


@pytest.mark.parametrize('initial_variables', [0, 1, 42])
def test_next_variables(create_cnf_builder, initial_variables):
    cnf_builder = create_cnf_builder(initial_variables)

    expected_variables = list(range(initial_variables + 1, initial_variables + 8))
    assert cnf_builder.next_variables(7) == expected_variables
    assert cnf_builder.number_of_variables == initial_variables + 7


@pytest.mark.parametrize('initial_variables', [0, 1, 42])
def test_add_clauses(create_cnf_builder, initial_variables):
    variable_1 = variable(15)
    variable_2 = variable(-16)

    cnf_builder = create_cnf_builder(initial_variables)
    tseitin_strategy = TseitinGateStrategy()

    result_and = tseitin_strategy.wire_and(variable_1, variable_2, cnf_builder)
    assert cnf_builder.number_of_variables == initial_variables + 1
    assert result_and == initial_variables + 1

    result_or = tseitin_strategy.wire_or(variable_1, variable_2, cnf_builder)
    assert cnf_builder.number_of_variables == initial_variables + 2
    assert result_or == initial_variables + 2

    expected_clauses = set()
    expected_clauses.update(and_equality(variable_1, variable_2, result_and))
    expected_clauses.update(or_equality(variable_1, variable_2, result_or))

    clauses = cnf_builder.build_clauses()
    assert any(result_and in clause for clause in clauses)
    assert any(result_or in clause for clause in clauses)
    assert clauses == expected_clauses


def test_build_clauses(create_cnf_builder):
    """Test that the tseitin encoding cannot construct clauses with
    duplicate variables.
    """
    cnf_builder = create_cnf_builder()

    clauses = xor_equality(variable(-1), variable(1), variable(-1))
    cnf_builder.append_clauses(clauses)

    clauses = equal_equality(variable(-1), variable(1), variable(-1))
    cnf_builder.append_clauses(clauses)

    assert not list(filter(has_duplicates, cnf_builder.build_clauses()))


def has_duplicates(clause) -> bool:
    return not isinstance(clause, frozenset) \
           or any(-x in clause for x in clause)


@pytest.mark.parametrize('constant_value', ['0', '1'])
def test_constant_propagation(create_cnf_builder, constant_value):
    var = variable(1)
    const = constant(constant_value)

    cnf_builder = create_cnf_builder()
    tseitin_strategy = TseitinGateStrategy()

    result_1 = tseitin_strategy.wire_and(var, const, cnf_builder)
    result_2 = tseitin_strategy.wire_and(const, var, cnf_builder)
    assert cnf_builder.number_of_variables == 0
    assert not cnf_builder.build_clauses()

    assert result_1 == result_2
    if const == '1':
        assert result_1 == var
    else:
        assert result_1 == const

    result_1 = tseitin_strategy.wire_or(var, const, cnf_builder)
    result_2 = tseitin_strategy.wire_or(const, var, cnf_builder)
    assert cnf_builder.number_of_variables == 0
    assert not cnf_builder.build_clauses()

    assert result_1 == result_2
    if const == '1':
        assert result_1 == const
    else:
        assert result_1 == var
