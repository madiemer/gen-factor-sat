import random
import sys
from dataclasses import dataclass
from math import ceil
from random import Random
from typing import List, Set, Optional, Tuple

from gen_factor_sat import strategies, utils
from gen_factor_sat.circuit import n_bit_equality
from gen_factor_sat.multiplication import karatsuba
from gen_factor_sat.tseitin import Clause, Variable


@dataclass
class FactoringSat:
    number: int
    factor_1: List[Variable]
    factor_2: List[Variable]
    number_of_variables: int
    clauses: Set[Clause]
    max_value: Optional[int] = None
    seed: Optional[int] = None

    def to_dimacs(self):
        comments = []
        if self.max_value:
            max_value = 'c Random number in range: 2 - {0}'.format(self.max_value)
            comments.append(max_value)

        if self.seed:
            seed = 'c Seed: {0}'.format(self.seed)
            comments.append(seed)

        if comments:
            comments.append('c')

        number = 'c Number: {0}'.format(self.number)
        factor_1 = 'c Factor 1: {0}'.format(self.factor_1)
        factor_2 = 'c Factor 2: {0}'.format(self.factor_2)
        comments.extend([number, factor_1, factor_2])

        comment_lines = '\n'.join(comments) + '\n'
        cnf_lines = result_to_dimacs(self.number_of_variables, self.clauses)

        return comment_lines + cnf_lines


def factorize_random_number(max_value: int, seed: Optional[int]) -> FactoringSat:
    if not seed:
        seed = random.randrange(sys.maxsize)

    number = _generate_number(max_value=max_value, seed=seed)
    factor_sat = factorize_number(number)
    factor_sat.seed = seed
    factor_sat.max_value = max_value

    return factor_sat


def factorize_number(number: int) -> FactoringSat:
    bin_number = utils.to_bin_list(number)

    tseitin_strategy = strategies.TseitinStrategy()

    factor_length_1, factor_length_2 = _factor_lengths(len(bin_number))
    sym_factor_1, sym_factor_2, mult_result = multiply_to_cnf(karatsuba, factor_length_1, factor_length_2,
                                                              tseitin_strategy)
    fact_result = n_bit_equality(list(bin_number), mult_result, tseitin_strategy)
    tseitin_strategy.assume(fact_result, tseitin_strategy.one())

    # For performance reasons it is better to check all clauses at
    # once instead of checking the clauses whenever they are added
    # clauses = set(filter(is_no_tautology, tseitin_strategy.clauses))

    return FactoringSat(
        number=number,
        factor_1=sym_factor_1,
        factor_2=sym_factor_2,
        number_of_variables=tseitin_strategy.number_of_variables,
        clauses=tseitin_strategy.clauses
    )


def _generate_number(max_value, seed: int) -> int:
    rand = Random(seed)
    return rand.randint(2, max_value)


def _factor_lengths(number_length: int) -> Tuple[int, int]:
    factor_length_1 = ceil(number_length / 2)
    factor_length_2 = number_length - 1

    return factor_length_1, factor_length_2


def multiply_to_cnf(multiply, factor_length_1, factor_length_2, tseitin_strategy):
    factor_1 = tseitin_strategy.next_variables(factor_length_1)
    factor_2 = tseitin_strategy.next_variables(factor_length_2)

    mult_result = multiply(factor_1, factor_2, tseitin_strategy)
    return factor_1, factor_2, mult_result


def result_to_dimacs(num_variables: int, clauses: Set[Clause]) -> str:
    problem = 'p cnf {0} {1}'.format(num_variables, len(clauses))
    return '\n'.join([problem] + list(map(clause_to_dimacs, clauses)))


def clause_to_dimacs(clause: Clause) -> str:
    if not clause:
        return '0'
    else:
        return ' '.join(map(str, clause)) + ' 0'
