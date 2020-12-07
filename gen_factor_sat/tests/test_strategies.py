import pytest

from gen_factor_sat.tseitin_encoding import variable, constant, and_equality, or_equality
from gen_factor_sat.tseitin_strategies import CNFBuilder, TseitinGateStrategy


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


@pytest.fixture()
def tseitin_strategy(create_cnf_builder):
    return TseitinGateStrategy(create_cnf_builder())


@pytest.fixture()
def eval_strategy():
    return EvalStrategy()


@pytest.mark.parametrize('initial_variables', [0, 1, 42])
def test_next_variables(create_cnf_builder, initial_variables):
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
    variable_1 = variable(1)
    variable_2 = variable(-2)

    cnf_builder = create_cnf_builder(initial_variables)
    tseitin_strategy = TseitinGateStrategy(cnf_builder)

    result_and = tseitin_strategy.wire_and(variable_1, variable_2)
    assert cnf_builder.number_of_variables == initial_variables + 1
    assert result_and == initial_variables + 1

    result_or = tseitin_strategy.wire_or(variable_1, variable_2)
    assert cnf_builder.number_of_variables == initial_variables + 2
    assert result_or == initial_variables + 2

    expected_clauses = set()
    expected_clauses.update(and_equality(variable_1, variable_2, result_and))
    expected_clauses.update(or_equality(variable_1, variable_2, result_or))

    assert any(result_and in clause for clause in cnf_builder.clauses)
    assert any(result_or in clause for clause in cnf_builder.clauses)
    assert cnf_builder.clauses == expected_clauses


@pytest.mark.parametrize('constant_value', ['0', '1'])
def test_constant_propagation(create_cnf_builder, constant_value):
    var = variable(1)
    const = constant(constant_value)

    cnf_builder = create_cnf_builder()
    tseitin_strategy = TseitinGateStrategy(cnf_builder)

    result_1 = tseitin_strategy.wire_and(var, const)
    result_2 = tseitin_strategy.wire_and(const, var)
    assert cnf_builder.number_of_variables == 0
    assert not cnf_builder.clauses

    assert result_1 == result_2
    if const == '1':
        assert result_1 == var
    else:
        assert result_1 == const

    result_1 = tseitin_strategy.wire_or(var, const)
    result_2 = tseitin_strategy.wire_or(const, var)
    assert cnf_builder.number_of_variables == 0
    assert not cnf_builder.clauses

    assert result_1 == result_2
    if const == '1':
        assert result_1 == const
    else:
        assert result_1 == var

# def test_equals_eval_strategy(tseitin_strategy, eval_strategy):
#     formula = CNF(from_clauses=tseitin_strategy.clauses)
#
#     tseitin_strategy.wire_and(x, y)
#
#
#
# def run_cnf(input_assignment, output_variables, clauses):
#     formula = CNF(clauses)
#
#     with Solver(name="cadical", bootstrap_with=formula) as solver:
#         solver.solve(assumptions=input_assignment)
#         model = solver.get_model()
#
#     result_assign = [(model[r - 1] >= 0 if r != '0' else False) for r in output_variables]
#     return list(map(lambda x: bin(x)[2:], result_assign))
