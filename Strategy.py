import heapq
import operator as op

import Gate
from Circuit import ZERO, ONE


class EvalStrategy:

    def wire_and(self, x, y):
        return bin((x == '1') and (y == '1'))[2:]

    def wire_or(self, x, y):
        return bin((x == '1') or (y == '1'))[2:]

    def wire_not(self, x):
        return bin(not (x == '1'))[2:]


class CircuitStrategy:

    def __init__(self):
        self.counter = 1

    def wire_and(self, x, y):
        if is_constant(x) or is_constant(y):
            return constant_and(x, y)
        else:
            self.counter += 1
            return Gate.AndGate(x, y)

    def wire_or(self, x, y):
        if is_constant(x) or is_constant(y):
            return constant_or(x, y)
        else:
            self.counter += 1
            return Gate.OrGate(x, y)

    def wire_not(self, x):
        if is_constant(x):
            return constant_not(x)
        else:
            self.counter += 1
            return Gate.NotGate(x)


class TseitinStrategy:

    def __init__(self, variables):
        self.variables = list(map(op.neg, variables))
        heapq.heapify(self.variables)

        self.clauses = set()

    def wire_and(self, x, y):
        if is_constant(x) or is_constant(y):
            return constant_and(x, y)
        else:
            # heapq does not support a max heap => Reverse order
            z = -self.variables[0] + 1
            heapq.heappush(self.variables, -z)

            self.clauses.update([frozenset([x, -z]), frozenset([y, -z]), frozenset([-x, -y, z])])
            return z

    def wire_or(self, x, y):
        if is_constant(x) or is_constant(y):
            return constant_or(x, y)
        else:
            # heapq does not support a max heap => Reverse order
            z = -self.variables[0] + 1
            heapq.heappush(self.variables, -z)

            self.clauses.update([frozenset([-x, y, z]), frozenset([x, -y, z]), frozenset([x, y, -z])])
            return z

    def wire_not(self, x):
        if is_constant(x):
            return constant_not(x)
        else:
            return -x


def is_constant(x):
    return x == ZERO or x == ONE


def constant_and(x, y):
    if x == ZERO or y == ZERO:
        return ZERO
    elif x == ONE:
        return y
    elif y == ONE:
        return x


def constant_or(x, y):
    if x == ONE or y == ONE:
        return ONE
    elif x == ZERO:
        return y
    elif y == ZERO:
        return x


def constant_not(x):
    if x == ZERO:
        return ONE
    elif x == ONE:
        return ZERO
