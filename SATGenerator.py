from math import ceil

import Strategy
import Tseitin
from Multiplication import karatsuba


def factoring_to_sat(number: int):
    bin_n = bin(number)[2:]

    len_x, len_y = factor_lengths(len(bin_n))
    sym_x, sym_y = create_symbolic_input(len_x, len_y)

    result, variables, clauses = mult_to_cnf(sym_x, sym_y)

    for c in result_equiv_number(result, bin_n):
        clauses.update(c)

    return sym_x, sym_y, variables, clauses


def factor_lengths(len_n: int):
    len_x = ceil(len_n / 2)
    len_y = len_n - 1

    return len_x, len_y


def create_symbolic_input(len_x: int, len_y: int):
    sym_x = list(range(1, len_x + 1))
    sym_y = list(range(len_x + 1, len_x + len_y + 1))

    return sym_x, sym_y


def mult_to_cnf(sym_x, sym_y):
    tseitin_strategy = Strategy.TseitinStrategy(sym_x + sym_y)
    result = karatsuba(sym_x, sym_y, tseitin_strategy)

    return result, tseitin_strategy.variables, tseitin_strategy.clauses


def result_equiv_number(result, number):
    aligned_number = '0' * (len(result) - len(number)) + number

    for n, z in zip(aligned_number, result):
        yield Tseitin.equality(n, z)
