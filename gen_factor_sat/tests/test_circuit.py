import pytest
from hypothesis import given, assume
from hypothesis.strategies import integers

from gen_factor_sat import strategies, circuit
from gen_factor_sat import utils


# @given(integers(min_value=0), integers(min_value=0), booleans())
@pytest.mark.parametrize('x, y, c', [(0, 0, '0'), (5, 7, '1'), (12, 35, '1')])
def test_n_bit_adder(x, y, c):
    bin_xs = utils.to_bin_list(x)
    bin_ys = utils.to_bin_list(y)
    # cs = bin(c)[2:]

    strategy = strategies.EvalStrategy()
    bin_result = circuit.n_bit_adder(bin_xs, bin_ys, c, strategy)

    assert len(bin_result) == max(len(bin_xs), len(bin_ys)) + 1
    assert utils.to_int(bin_result) == x + y + int(c)


@given(integers(min_value=0), integers(min_value=0))
def test_subtract(x, y):
    assume(x >= y)
    bin_xs = utils.to_bin_list(x)
    bin_ys = utils.to_bin_list(y)

    strategy = strategies.EvalStrategy()
    bin_result = circuit.subtract(bin_xs, bin_ys, strategy)

    assert len(bin_result) == max(len(bin_xs), len(bin_ys))
    assert utils.to_int(bin_result) == x - y


@given(integers(min_value=0), integers(min_value=0))
def test_n_bit_equality(x, y):
    bin_xs = utils.to_bin_list(x)
    bin_ys = utils.to_bin_list(y)

    strategy = strategies.EvalStrategy()
    bin_result = circuit.n_bit_equality(bin_xs, bin_ys, strategy)

    assert (bin_result == '1') == (x == y)


@given(integers(min_value=0), integers(min_value=0))
def test_align(xs, ys):
    bin_xs = utils.to_bin_list(xs)
    bin_ys = utils.to_bin_list(ys)

    strategy = strategies.EvalStrategy()
    aligned_xs, aligned_ys = circuit.align(bin_xs, bin_ys, strategy)

    assert len(aligned_xs) == max(len(bin_xs), len(bin_ys))
    assert len(aligned_ys) == max(len(bin_xs), len(bin_ys))

    assert utils.to_int(aligned_xs) == xs
    assert utils.to_int(aligned_ys) == ys


@given(integers(min_value=0), integers(min_value=0, max_value=10))
def test_shift(xs, shifts):
    bin_xs = utils.to_bin_list(xs)

    strategy = strategies.EvalStrategy()
    shifted_xs = circuit.shift(bin_xs, shifts, strategy)

    assert len(shifted_xs) == len(bin_xs) + shifts
    assert utils.to_int(shifted_xs) == (2 ** shifts) * xs
