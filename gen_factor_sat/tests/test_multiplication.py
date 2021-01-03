import pytest
from hypothesis import given, assume
from hypothesis.strategies import integers
from pysat.formula import CNF
from pysat.solvers import Solver

import gen_factor_sat.tests.utils as test_utils
from gen_factor_sat import utils
from gen_factor_sat.circuit.instances import ConstantFactoringStrategy, ConstantWallaceFactoringStrategy, \
    TseitinFactoringStrategy, TseitinWallaceFactoringStrategy
from gen_factor_sat.circuit.tseitin.circuit import CNFBuilder


@pytest.fixture(scope='module')
def constant_strategy():
    return ConstantFactoringStrategy()


@pytest.fixture(scope='module')
def constant_wallace_strategy():
    return ConstantWallaceFactoringStrategy()


@pytest.fixture(scope='module')
def tseitin_strategy():
    return TseitinFactoringStrategy()


@pytest.fixture(scope='module')
def tseitin_wallace_strategy():
    return TseitinWallaceFactoringStrategy()


@given(factor_1=integers(0, 2 ** 40), factor_2=integers(0, 2 ** 40))
def test_wallace(constant_wallace_strategy, factor_1, factor_2):
    assert run_eval_mult(constant_wallace_strategy, factor_1, factor_2) == factor_1 * factor_2


@given(factor_1=integers(0, 2 ** 60), factor_2=integers(0, 2 ** 60))
def test_karatsuba(constant_strategy, factor_1, factor_2):
    assert run_eval_mult(constant_strategy, factor_1, factor_2) == factor_1 * factor_2


@given(factor_1=integers(2 ** 21, 2 ** 60), factor_2=integers(0, 2 ** 30))
def test_split_simplification(constant_strategy, factor_1, factor_2):
    assume(len(utils.to_bin_list(factor_1)) > 2 * len(utils.to_bin_list(factor_2)))
    assert run_eval_mult(constant_strategy, factor_1, factor_2) == factor_1 * factor_2


@pytest.mark.parametrize('factor_1', [1, 17, 2 ** 10 + 865, 2 ** 21 + 46196])
@pytest.mark.parametrize('factor_2', [0, 2, 2 ** 21 + 510579])
def test_tseitin_wallace_mult(tseitin_wallace_strategy, factor_1, factor_2):
    assert run_tseitin_mult(tseitin_wallace_strategy, factor_1, factor_2) == factor_1 * factor_2


@pytest.mark.parametrize('factor_1', [1, 17, 2 ** 10 + 865, 2 ** 21 + 46196])
@pytest.mark.parametrize('factor_2', [0, 2, 2 ** 21 + 510579])
def test_tseitin_mult(tseitin_strategy, factor_1, factor_2):
    assert run_tseitin_mult(tseitin_strategy, factor_1, factor_2) == factor_1 * factor_2


def run_eval_mult(circuit, factor_1, factor_2):
    bin_factor_1 = utils.to_bin_list(factor_1)
    bin_factor_2 = utils.to_bin_list(factor_2)

    bin_result = circuit.multiply(bin_factor_1, bin_factor_2, None)

    return utils.to_int(bin_result)


def run_tseitin_mult(tseitin_circuit, factor_1, factor_2):
    cnf_builder = CNFBuilder()

    bin_factor_1 = utils.to_bin_list(factor_1)
    bin_factor_2 = utils.to_bin_list(factor_2)

    factor_1 = cnf_builder.next_variables(len(bin_factor_1))
    factor_2 = cnf_builder.next_variables(len(bin_factor_2))

    result = tseitin_circuit.multiply(factor_1, factor_2, cnf_builder)

    assignment_1 = list(test_utils.assign(factor_1, bin_factor_1))
    assignment_2 = list(test_utils.assign(factor_2, bin_factor_2))

    bin_result = test_utils.run_cnf(assignment_1 + assignment_2, result, cnf_builder.build_clauses())
    assert bin_result is not None, 'The formula should always have satisfying assignment'

    return utils.to_int(bin_result)
