import operator
import itertools
import collections

class Strategy:

    def mult(self, x, y):
        return self.with_int(operator.mul, x, y)

    def add(self, x, y):
        return self.with_int(operator.add, x, y)

    def subtract(self, x, y):
        return self.with_int(operator.sub, x, y)

    def shift(self, x, n):
        return x + '0' * n

    def int_to_bin(self, x):
        return bin(x)[2:]

    def bin_to_int(self, x):
        if x == '':
            return 0
        else:
            return int(x, 2)

    def with_int(self, func2, x, y):
        x_int = self.bin_to_int(x)
        y_int = self.bin_to_int(y)

        z_int = func2(x_int, y_int)

        return self.int_to_bin(z_int)


# x,y in binary
def karatsuba(x, y, strategy):
    if len(x) < 4 or len(y) < 4:
        return strategy.mult(x, y)

    n = max(len(x), len(y))
    half = (n + 1) // 2

    x1 = x[:-half]
    x0 = x[-half:]

    y1 = y[:-half]
    y0 = y[-half:]

    z0 = karatsuba(x0, y0, strategy)
    z2 = karatsuba(x1, y1, strategy)

    z1 = karatsuba(strategy.add(x1, x0), strategy.add(y1, y0), strategy)
    z1 = strategy.subtract(strategy.subtract(z1, z2), z0)

    return strategy.add(strategy.add(strategy.shift(z2, 2 * half), strategy.shift(z1, half)), z0)

