import random
import sys
from dataclasses import dataclass
from math import ceil
from random import Random
from typing import List, Set, Optional, Tuple

from gen_factor_sat import strategies
from gen_factor_sat.circuit import n_bit_equality
from gen_factor_sat.multiplication import karatsuba
from gen_factor_sat.tseitin import Symbol, Clause, Variable, ONE, is_no_tautology

@dataclass
class FactoringSat:
    number: int
    factor_1: List[Symbol]
    factor_2: List[Symbol]
    num_variables: int
    clauses: Set[Clause]
    seed: Optional[int] = None

    def to_dimacs(self):
        if not self.seed:
            number = 'c Number: {0}'.format(self.number)
        else:
            number = 'c Seed: {0} (Number: {1})'.format(self.seed, self.number)

        factor_1 = 'c Factor 1: {0}'.format(self.factor_1)
        factor_2 = 'c Factor 2: {0}'.format(self.factor_2)

        return '\n'.join([number, factor_1, factor_2]) + '\n' + result_to_dimacs(self.num_variables, self.clauses)


def factorize_random_number(seed: Optional[int]) -> FactoringSat:
    if not seed:
        seed = random.randrange(sys.maxsize)

    number = _generate_number(seed=seed)
    factor_sat = factorize_number(number)
    factor_sat.seed = seed

    return factor_sat


def factorize_number(number: int) -> FactoringSat:
    bin_n = bin(number)[2:]

    len_x, len_y = _factor_lengths(len(bin_n))
    sym_x, sym_y = create_symbolic_input(len_x, len_y)

    tseitin_strategy = strategies.TseitinStrategy(sym_x + sym_y)
    mult_result = karatsuba(sym_x, sym_y, tseitin_strategy)
    fact_result = n_bit_equality(list(bin_n), mult_result, tseitin_strategy)
    tseitin_strategy.assume(fact_result, ONE)

    # For performance reasons it is better to check all clauses at
    # once instead of checking the clauses whenever they are added
    clauses = set(filter(is_no_tautology, tseitin_strategy.clauses))

    return FactoringSat(number, sym_x, sym_y, tseitin_strategy.num_variables, clauses)


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


def result_to_dimacs(num_variables: int, clauses: Set[Clause]) -> str:
    problem = 'p cnf {0} {1}'.format(num_variables, len(clauses))
    return '\n'.join([problem] + list(map(clause_to_dimacs, clauses)))


def clause_to_dimacs(clause: Clause) -> str:
    return ' '.join(map(str, clause)) + ' 0'
