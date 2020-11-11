import Circuit
import WallaceTree
from Circuit import ZERO


def karatsuba(xs, ys, circuit):
    if len(xs) < 20 or len(ys) < 20:
        return WallaceTree.wallace_tree(xs, ys, circuit)

    n = max(len(xs), len(ys))
    half = (n + 1) // 2

    x1 = xs[:-half]
    x0 = xs[-half:]

    y1 = ys[:-half]
    y0 = ys[-half:]

    z0 = karatsuba(x0, y0, circuit)
    z2 = karatsuba(x1, y1, circuit)

    # z1 = karatsuba((x1 + x0), (y1 + y0)) - z2 - z0
    sum_x = Circuit.n_bit_adder(x1, x0, ZERO, circuit)
    sum_y = Circuit.n_bit_adder(y1, y0, ZERO, circuit)

    z1 = karatsuba(sum_x, sum_y, circuit)
    z1 = Circuit.subtract(z1, z2, circuit)
    z1 = Circuit.subtract(z1, z0, circuit)

    # x * y = z2 * 2^(2 * half) + z1 * 2^(half) + z0
    sum = Circuit.n_bit_adder(Circuit.shift(z2, half), z1, ZERO, circuit)
    sum = Circuit.n_bit_adder(Circuit.shift(sum, half), z0, ZERO, circuit)

    return sum
