from math import ceil

import Strategy
import Tseitin
from Multiplication import karatsuba


def fakt_to_sat(number):
    bin_n = bin(number)[2:]

    len_x = ceil(len(bin_n) / 2)
    len_y = len(bin_n) - 1

    sym_x = list(range(1, len_x + 1))
    sym_y = list(range(len_x + 1, len_x + len_y + 1))

    tseitin_strategy = Strategy.TseitinStrategy(sym_x + sym_y)
    result = karatsuba(sym_x, sym_y, tseitin_strategy)

    aligned_number = '0' * (len(result) - len(bin_n)) + bin_n
    for n, z in zip(aligned_number, result):
        tseitin_strategy.clauses.union(Tseitin.equality(n, z))

    return tseitin_strategy.variables, tseitin_strategy.clauses
