import random
import sys
from abc import ABC
from dataclasses import dataclass
from math import ceil
from random import Random
from typing import List, Sequence, Set, Optional, Tuple, Generic, TypeVar

from gen_factor_sat import utils
from gen_factor_sat.circuit import NBitCircuitStrategy, ConstantStrategy, GeneralSimpleCircuitStrategy, \
    GeneralNBitCircuitStrategy
from gen_factor_sat.multiplication import MultiplicationStrategy, KaratsubaStrategy, WallaceTreeStrategy
from gen_factor_sat.tseitin_encoding import Symbol, Constant, Clause, Variable, is_no_tautology
from gen_factor_sat.tseitin_strategies import TseitinGateStrategy, CNFBuilder, TseitinCircuitStrategy

# Multiplier = Callable[[List[Symbol], List[Symbol], TseitinStrategy], List[Symbol]]
# Multiplication = namedtuple('Multiplication', ['factor_1', 'factor_2', 'result'])


T = TypeVar('T')
W = TypeVar('W')


class FactoringCircuit(Generic[T, W], NBitCircuitStrategy[T, W], MultiplicationStrategy[T, W], ABC):

    def factorize(self, factor_1: Sequence[T], factor_2: Sequence[T], number: Sequence[T], writer: W = None) -> T:
        mult_result = self.multiply(factor_1, factor_2, writer)
        fact_result = self.n_bit_equality(mult_result, number, writer)
        return fact_result


class TseitinFactoringStrategy(
    TseitinGateStrategy,
    TseitinCircuitStrategy,
    GeneralNBitCircuitStrategy[Symbol, CNFBuilder],
    WallaceTreeStrategy[Symbol, CNFBuilder],
    KaratsubaStrategy[Symbol, CNFBuilder],
    FactoringCircuit[Symbol, CNFBuilder]
):
    pass


class ConstantFactoringStrategy(
    ConstantStrategy,
    GeneralSimpleCircuitStrategy[Constant, None],
    GeneralNBitCircuitStrategy[Constant, None],
    WallaceTreeStrategy[Constant, None],
    KaratsubaStrategy[Constant, None],
    FactoringCircuit[Constant, None]
):
    pass


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
    cnf_builder = CNFBuilder()
    factoring_circuit = TseitinFactoringStrategy()

    bin_number = utils.to_bin_list(number)
    factor_length_1, factor_length_2 = _factor_lengths(len(bin_number))

    factor_1 = cnf_builder.next_variables(factor_length_1)
    factor_2 = cnf_builder.next_variables(factor_length_2)

    fact_result = factoring_circuit.factorize(factor_1, factor_2, bin_number, cnf_builder)
    factoring_circuit.assume(fact_result, factoring_circuit.one, cnf_builder)

    return FactoringSat(
        number=number,
        factor_1=factor_1,
        factor_2=factor_2,
        number_of_variables=cnf_builder.number_of_variables,
        clauses=cnf_builder.build_clauses()
    )

def _generate_number(max_value, seed: int) -> int:
    rand = Random(seed)
    return rand.randint(2, max_value)


def _factor_lengths(number_length: int) -> Tuple[int, int]:
    factor_length_1 = ceil(number_length / 2)
    factor_length_2 = number_length - 1

    return factor_length_1, factor_length_2


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
