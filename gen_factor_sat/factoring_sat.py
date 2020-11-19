import random
import sys
from dataclasses import dataclass
from math import ceil
from random import Random
from typing import List, Set, Optional, Tuple, Iterator

from gen_factor_sat import strategies, tseitin
from gen_factor_sat.multiplication import karatsuba
from gen_factor_sat.tseitin import Symbol, Clause, Variable


@dataclass
class FactorSat:
    number: int
    factor_1: List[Symbol]
    factor_2: List[Symbol]
    variables: Set[Symbol]
    clauses: Set[Clause]
    seed: Optional[int] = None

    def to_dimacs(self):
        if not self.seed:
            number = 'c Number: {0}'.format(self.number)
        else:
            number = 'c Seed: {0} (Number: {1})'.format(self.seed, self.number)

        factor_1 = 'c Factor 1: {0}'.format(self.factor_1)
        factor_2 = 'c Factor 2: {0}'.format(self.factor_2)

        return '\n'.join([number, factor_1, factor_2]) + '\n' + result_to_dimacs(self.variables, self.clauses)


def generate_factoring_to_sat(seed: Optional[int]) -> FactorSat:
    if not seed:
        seed = random.randrange(sys.maxsize)

    number = _generate_number(seed=seed)
    factor_sat = factoring_to_sat(number)
    factor_sat.seed = seed

    return factor_sat


def factoring_to_sat(number: int) -> FactorSat:
    bin_n = bin(number)[2:]

    len_x, len_y = _factor_lengths(len(bin_n))
    sym_x, sym_y = create_symbolic_input(len_x, len_y)

    result, variables, clauses = mult_to_cnf(sym_x, sym_y)

    for c in result_equiv_number(result, bin_n):
        clauses.update(c)

    return FactorSat(number, sym_x, sym_y, variables, clauses)


def _generate_number(seed: int) -> int:
    rand = Random(seed)
    return rand.randint(2, sys.maxsize)


def _factor_lengths(len_n: int) -> Tuple[int, int]:
    len_x = ceil(len_n / 2)
    len_y = len_n - 1

    return len_x, len_y


def create_symbolic_input(len_x: int, len_y: int) -> Tuple[List[Variable], List[Variable]]:
    sym_x = list(range(1, len_x + 1))
    sym_y = list(range(len_x + 1, len_x + len_y + 1))

    return sym_x, sym_y


def mult_to_cnf(sym_x: List[Variable], sym_y: List[Variable]) -> Tuple[List[Symbol], Set[Variable], Set[Clause]]:
    tseitin_strategy = strategies.TseitinStrategy(sym_x + sym_y)
    result = karatsuba(sym_x, sym_y, tseitin_strategy)

    return result, tseitin_strategy.variables, tseitin_strategy.clauses


def result_equiv_number(result: List[Symbol], number: str) -> Iterator[Set[Clause]]:
    aligned_number = '0' * (len(result) - len(number)) + number

    for n, z in zip(aligned_number, result):
        yield tseitin.equality(n, z)


def result_to_dimacs(variables: Set[Variable], clauses: Set[Clause]) -> str:
    problem = 'p {0} {1}'.format(len(variables), len(clauses))
    return '\n'.join([problem] + list(map(clause_to_dimacs, clauses)))


def clause_to_dimacs(clause: Clause) -> str:
    return ' '.join(map(str, clause)) + ' 0'
