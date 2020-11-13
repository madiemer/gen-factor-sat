Constant = str

ZERO = '0'
ONE = '1'


def half_adder(x, y, circuit):
    sum = circuit.wire_or(
        circuit.wire_and(x, circuit.wire_not(y)),
        circuit.wire_and(circuit.wire_not(x), y)
    )

    carry = circuit.wire_and(x, y)

    return sum, carry


def full_adder(x, y, c, circuit):
    partial_sum, carry_1 = half_adder(x, y, circuit)
    total_sum, carry_2 = half_adder(partial_sum, c, circuit)

    carry = circuit.wire_or(carry_1, carry_2)

    return total_sum, carry


def n_bit_adder(xs, ys, c, circuit):
    if not xs:
        return propagate(ys, c, circuit)
    elif not ys:
        return propagate(xs, c, circuit)
    else:
        x = xs[-1]
        y = ys[-1]
        sum_xy, carry_xy = full_adder(x, y, c, circuit)

        sum = n_bit_adder(xs[:-1], ys[:-1], carry_xy, circuit)
        return sum + [sum_xy]


def propagate(xs, c, circuit):
    if not xs:
        return [c]
    else:
        x = xs[-1]
        partial_sum, carry = half_adder(x, c, circuit)
        total_sum = propagate(xs[:-1], carry, circuit)

        return total_sum + [partial_sum]


def subtract(xs, ys, circuit):
    aligned = ([ZERO] * (len(xs) - len(ys))) + ys
    complement = list(map(circuit.wire_not, aligned))

    sum = n_bit_adder(xs, complement, ONE, circuit)
    return sum[1:]  # Carry is not needed


def shift(xs, n):
    return xs + [ZERO] * n
