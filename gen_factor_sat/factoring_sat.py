import random
import sys
from collections import namedtuple
from dataclasses import dataclass
from math import ceil
from random import Random
from typing import List, Set, Optional, Tuple, Callable

from gen_factor_sat import strategies, utils
from gen_factor_sat.circ_build import TseitinStrategy, CNFBuilder
from gen_factor_sat.multiplication import KaratsubaMultiplication, WallaceTreeMultiplier
from gen_factor_sat.tseitin import Clause, Variable, Symbol, is_no_tautology

Multiplier = Callable[[List[Symbol], List[Symbol], TseitinStrategy], List[Symbol]]
Multiplication = namedtuple('Multiplication', ['factor_1', 'factor_2', 'result'])


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
            max_value = 'Random number in range: 2 - {0}'.format(self.max_value)
            comments.append(max_value)

        if self.seed:
            seed = 'Seed: {0}'.format(self.seed)
            comments.append(seed)

        if comments:
            comments.append('')

        number = 'Factorization of the number: {0}'.format(self.number)
        factor_1 = 'Factor 1 is encoded in the variables: {0}'.format(self.factor_1)
        factor_2 = 'Factor 2 is encoded in the variables: {0}'.format(self.factor_2)
        comments.extend([number, factor_1, factor_2])

        return cnf_to_dimacs(self.number_of_variables, self.clauses, comments=comments)


def factorize_random_number(max_value: int, seed: Optional[int]) -> FactoringSat:
    if seed is None:
        seed = random.randrange(sys.maxsize)

    number = _generate_number(max_value=max_value, seed=seed)
    factor_sat = factorize_number(number)
    factor_sat.seed = seed
    factor_sat.max_value = max_value

    return factor_sat


def factorize_number(number: int) -> FactoringSat:
    bin_number = utils.to_bin_list(number)
    factor_length_1, factor_length_2 = _factor_lengths(len(bin_number))

    cnf_builder = CNFBuilder()
    circuit = TseitinStrategy(cnf_builder)
    wallace_mult = WallaceTreeMultiplier(circuit)
    karatsuba = KaratsubaMultiplication(circuit, wallace_mult)

    factor_1 = cnf_builder.next_variables(factor_length_1)
    factor_2 = cnf_builder.next_variables(factor_length_2)

    mult_result = karatsuba.multiply(factor_1, factor_2)

    #sym_mult = multiply_to_cnf(karatsuba, factor_length_1, factor_length_2, circuit)
    fact_result = circuit.n_bit_equality(mult_result, bin_number)
    circuit.assume(fact_result, circuit.one())

    # For performance reasons it is better to check all clauses at
    # once instead of checking the clauses whenever they are added
    clauses = set(filter(is_no_tautology, cnf_builder.clauses))

    return FactoringSat(
        number=number,
        factor_1=factor_1,
        factor_2=factor_2,
        number_of_variables=cnf_builder.number_of_variables,
        clauses=clauses
    )


def _generate_number(max_value, seed: int) -> int:
    rand = Random(seed)
    return rand.randint(2, max_value)


def _factor_lengths(number_length: int) -> Tuple[int, int]:
    factor_length_1 = ceil(number_length / 2)
    factor_length_2 = number_length - 1

    return factor_length_1, factor_length_2


def multiply_to_cnf(
        multiply: Multiplier,
        factor_length_1: int,
        factor_length_2: int,
        tseitin_strategy: TseitinStrategy):
    factor_1 = tseitin_strategy.next_variables(factor_length_1)
    factor_2 = tseitin_strategy.next_variables(factor_length_2)

    mult_result = multiply(factor_1, factor_2, tseitin_strategy)
    return Multiplication(factor_1, factor_2, mult_result)


def cnf_to_dimacs(num_variables: int, clauses: Set[Clause], comments=None) -> str:
    if (comments is None) or (not comments):
        comment_lines = ''
    else:
        prefixed_comments = list(map('c {0}'.format, comments))
        comment_lines = '\n'.join(prefixed_comments) + '\n'

    problem = 'p cnf {0} {1}'.format(num_variables, len(clauses))
    dimacs_clauses = list(map(clause_to_dimacs, clauses))
    cnf_lines = '\n'.join([problem] + dimacs_clauses)

    return comment_lines + cnf_lines


def clause_to_dimacs(clause: Clause) -> str:
    if not clause:
        return '0'
    else:
        return ' '.join(map(str, clause)) + ' 0'
