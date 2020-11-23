from gen_factor_sat import strategies, circuit
import pytest


@pytest.mark.parametrize('x, y, c', [(0, 0, '0'), (5, 7, '1'), (12, 35, '1')])
def test_n_bit_adder(x, y, c):
    xs = list(bin(x)[2:])
    ys = list(bin(y)[2:])

    strategy = strategies.EvalStrategy()
    bin_result = circuit.n_bit_adder(xs, ys, c, strategy)

    assert int(''.join(bin_result), 2) == x + y + int(c)
