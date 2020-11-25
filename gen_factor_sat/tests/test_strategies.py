import pytest

from gen_factor_sat import strategies, tseitin


@pytest.fixture()
def create_tseitin_strategy():
    def _create_tseitin_strategy(initial_variables=0):
        if initial_variables is 0:
            tseitin_strategy = strategies.TseitinStrategy()
        else:
            tseitin_strategy = strategies.TseitinStrategy(initial_variables)

        assert tseitin_strategy.number_of_variables == initial_variables
        return tseitin_strategy

    return _create_tseitin_strategy


@pytest.fixture()
def tseitin_strategy(create_tseitin_strategy):
    return create_tseitin_strategy()


@pytest.fixture()
def eval_strategy():
    return strategies.EvalStrategy()


@pytest.mark.parametrize('initial_variables', [0, 1, 42])
def test_next_variables(create_tseitin_strategy, initial_variables):
    tseitin_strategy = create_tseitin_strategy(initial_variables)

    for i in range(20):
        assert tseitin_strategy.next_variable() == initial_variables + i + 1
        assert tseitin_strategy.number_of_variables == initial_variables + i + 1


@pytest.mark.parametrize('initial_variables', [0, 1, 42])
def test_next_variables(create_tseitin_strategy, initial_variables):
    tseitin_strategy = create_tseitin_strategy(initial_variables)

    expected_variables = list(range(initial_variables + 1, initial_variables + 8))
    assert tseitin_strategy.next_variables(7) == expected_variables
    assert tseitin_strategy.number_of_variables == initial_variables + 7


def test_add_clauses(tseitin_strategy):
    variable_1 = 1
    variable_2 = -2

    result_and = tseitin_strategy.wire_and(variable_1, variable_2)
    assert result_and == 1

    result_or = tseitin_strategy.wire_or(variable_1, variable_2)
    assert result_or == 2

    expected_clauses = set()
    expected_clauses.update(tseitin.and_equality(variable_1, variable_2, result_and))
    expected_clauses.update(tseitin.or_equality(variable_1, variable_2, result_or))
    assert tseitin_strategy.clauses == expected_clauses


@pytest.mark.parametrize('constant', ['0', '1'])
def test_constant_propagation(tseitin_strategy, constant):
    variable = 1

    result_1 = tseitin_strategy.wire_and(variable, constant)
    result_2 = tseitin_strategy.wire_and(constant, variable)
    assert tseitin_strategy.number_of_variables == 0
    assert not tseitin_strategy.clauses

    assert result_1 == result_2
    if constant == '1':
        assert result_1 == variable
    else:
        assert result_1 == constant

    result_1 = tseitin_strategy.wire_or(variable, constant)
    result_2 = tseitin_strategy.wire_or(constant, variable)
    assert tseitin_strategy.number_of_variables == 0
    assert not tseitin_strategy.clauses

    assert result_1 == result_2
    if constant == '1':
        assert result_1 == constant
    else:
        assert result_1 == variable

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
