import pytest
from hypothesis import given, assume
from hypothesis.strategies import integers, booleans

from gen_factor_sat import utils
from gen_factor_sat.circuit.instances import TseitinFactoringStrategy


@pytest.fixture(scope='module')
def tseitin_circuit():
    return TseitinFactoringStrategy()


@given(number_1=integers(min_value=0), number_2=integers(min_value=0), carry=booleans())
def test_n_bit_adder(tseitin_circuit, number_1, number_2, carry):
    bin_number_1 = utils.to_bin_list(number_1)
    bin_number_2 = utils.to_bin_list(number_2)
    bin_carry = utils.to_bin_list(carry)[0]

    bin_result = tseitin_circuit.n_bit_adder(bin_number_1, bin_number_2, bin_carry, None)

    assert len(bin_result) == max(len(bin_number_1), len(bin_number_2)) + 1
    assert utils.to_int(bin_result) == number_1 + number_2 + int(carry)


@given(number_1=integers(min_value=0), number_2=integers(min_value=0))
def test_subtract(tseitin_circuit, number_1, number_2):
    assume(number_1 >= number_2)
    bin_number_1 = utils.to_bin_list(number_1)
    bin_number_2 = utils.to_bin_list(number_2)

    bin_result = tseitin_circuit.subtract(bin_number_1, bin_number_2, None)

    assert len(bin_result) == max(len(bin_number_1), len(bin_number_2))
    assert utils.to_int(bin_result) == number_1 - number_2


@given(number_1=integers(min_value=0), number_2=integers(min_value=0))
def test_n_bit_equality(tseitin_circuit, number_1, number_2):
    bin_number_1 = utils.to_bin_list(number_1)
    bin_number_2 = utils.to_bin_list(number_2)

    bin_result = tseitin_circuit.n_bit_equality(bin_number_1, bin_number_2, None)

    assert (bin_result == '1') == (number_1 == number_2)


@given(number_1=integers(min_value=0), number_2=integers(min_value=0))
def test_align(tseitin_circuit, number_1, number_2):
    bin_number_1 = utils.to_bin_list(number_1)
    bin_number_2 = utils.to_bin_list(number_2)

    aligned_xs, aligned_ys = tseitin_circuit.align(bin_number_1, bin_number_2, None)

    assert len(aligned_xs) == max(len(bin_number_1), len(bin_number_2))
    assert len(aligned_ys) == max(len(bin_number_1), len(bin_number_2))

    assert utils.to_int(aligned_xs) == number_1
    assert utils.to_int(aligned_ys) == number_2


@given(number=integers(min_value=0), shifts=integers(min_value=0, max_value=10))
def test_shift(tseitin_circuit, number, shifts):
    bin_number = utils.to_bin_list(number)

    shifted_xs = tseitin_circuit.shift(bin_number, shifts, None)

    assert len(shifted_xs) == len(bin_number) + shifts
    assert utils.to_int(shifted_xs) == (2 ** shifts) * number
