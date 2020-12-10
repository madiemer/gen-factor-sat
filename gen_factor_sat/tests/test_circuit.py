import pytest
from hypothesis import given, assume
from hypothesis.strategies import integers

from gen_factor_sat import utils
from gen_factor_sat.factoring_sat import ConstantFactoringStrategy


@pytest.fixture()
def tseitin_circuit():
    return ConstantFactoringStrategy()

#
# @given(integers(), randoms())
# def test_model(number, random: Random):
#     cnf_builder = CNFBuilder()
#     gate_strategy = TseitinGateStrategy(cnf_builder)
#
#     simple_circuit = TseitinCircuitStrategy(
#         cnf_builder=cnf_builder,
#         gate_strategy=gate_strategy
#     )
#
#     n_bit_circuit = GeneralNBitCircuitStrategy(
#         gate_strategy=gate_strategy,
#         circuit_strategy=simple_circuit
#     )
#
#     constant_gate_strategy = ConstantStrategy()
#     constant_simple_circuit = GeneralSimpleCircuitStrategy(gate_strategy=constant_gate_strategy)
#     constant_n_bit_circuit = GeneralNBitCircuitStrategy(gate_strategy=constant_gate_strategy, circuit_strategy=constant_simple_circuit)
#
#     bin_number = utils.to_bin_list(number)
#     result = []
#     for i in bin_number:
#         if random.random() <= 0.5:
#             var = random.randrange(1, len(bin_number) + 1)
#             result.append(tseitin_encoding.variable(var))
#         else:
#             result.append(tseitin_encoding.constant(i))
#
#     result.reverse()
#
#     result = n_bit_circuit.n_bit_adder(result, [], '0')
#
#     assignment_1 = list(assign(factor_1, bin_factor_1))
#     assignment_2 = list(assign(factor_2, bin_factor_2))
#
#     bin_result = run_cnf(assignment_1 + assignment_2, result, cnf_builder.clauses)
#
#     return utils.to_int(bin_result)
#
#     assert n_bit_circuit.n_bit_adder() == constant_n_bit_circuit.n_bit_adder()
#
#
# def symbolic(sym: str, random: Random):
#     if random.random() <= 0.5:
#         return tseitin_encoding.variable()


# @given(integers(min_value=0), integers(min_value=0), booleans())
@pytest.mark.parametrize('x, y, c', [(0, 0, '0'), (5, 7, '1'), (12, 35, '1')])
def test_n_bit_adder(tseitin_circuit, x, y, c):
    bin_xs = utils.to_bin_list(x)
    bin_ys = utils.to_bin_list(y)

    bin_result = tseitin_circuit.n_bit_adder(bin_xs, bin_ys, c)

    assert len(bin_result) == max(len(bin_xs), len(bin_ys)) + 1
    assert utils.to_int(bin_result) == x + y + int(c)


@given(x=integers(min_value=0), y=integers(min_value=0))
def test_subtract(tseitin_circuit, x, y):
    assume(x >= y)
    bin_xs = utils.to_bin_list(x)
    bin_ys = utils.to_bin_list(y)

    bin_result = tseitin_circuit.subtract(bin_xs, bin_ys)

    assert len(bin_result) == max(len(bin_xs), len(bin_ys))
    assert utils.to_int(bin_result) == x - y


@given(x=integers(min_value=0), y=integers(min_value=0))
def test_n_bit_equality(tseitin_circuit, x, y):
    bin_xs = utils.to_bin_list(x)
    bin_ys = utils.to_bin_list(y)

    bin_result = tseitin_circuit.n_bit_equality(bin_xs, bin_ys)

    assert (bin_result == '1') == (x == y)


@given(xs=integers(min_value=0), ys=integers(min_value=0))
def test_align(tseitin_circuit, xs, ys):
    bin_xs = utils.to_bin_list(xs)
    bin_ys = utils.to_bin_list(ys)

    aligned_xs, aligned_ys = tseitin_circuit.align(bin_xs, bin_ys)

    assert len(aligned_xs) == max(len(bin_xs), len(bin_ys))
    assert len(aligned_ys) == max(len(bin_xs), len(bin_ys))

    assert utils.to_int(aligned_xs) == xs
    assert utils.to_int(aligned_ys) == ys


@given(xs=integers(min_value=0), shifts=integers(min_value=0, max_value=10))
def test_shift(tseitin_circuit, xs, shifts):
    bin_xs = utils.to_bin_list(xs)

    shifted_xs = tseitin_circuit.shift(bin_xs, shifts)

    assert len(shifted_xs) == len(bin_xs) + shifts
    assert utils.to_int(shifted_xs) == (2 ** shifts) * xs
