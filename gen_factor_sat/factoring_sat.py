import math
import random
import sys
from dataclasses import dataclass
from typing import List, Set, Optional, Tuple, cast

from gen_factor_sat import utils
from gen_factor_sat.circuit.instances import TseitinFactoringStrategy
from gen_factor_sat.circuit.tseitin.circuit import CNFBuilder
from gen_factor_sat.circuit.tseitin.encoding import Clause, Symbol, Variable
from gen_factor_sat.number_generator import generate_number, NumberType, Number, fold_number_type

VERSION = '0.3'


@dataclass
class FactoringSat:
    number: Number
    factor_1: List[Variable]
    factor_2: List[Variable]
    number_of_variables: int
    clauses: Set[Clause]
    max_value: Optional[int] = None
    min_value: Optional[int] = None
    seed: Optional[int] = None

    def to_dimacs(self):
        comments = []
        comments.append('GenFactorSat v{0}'.format(VERSION))

        if self.max_value:
            interval = '[{0}, {1}]'.format(self.min_value, self.max_value)
            comments.append('The number was (pseudo-) randomly chosen from the interval: ' + interval)

            number_type = fold_number_type(
                self.number.number_type,
                f_prime='The number is a prime number.',
                f_prob_prime='The number is a prime number with an error probability less or equal to {0}.'.format,
                f_comp='The number is a composite number.',
                f_prob_comp=lambda x: 'The number is a composite number.',
                f_unknown=''
            )

            if number_type:
                comments.append(number_type)

            command = 'gen_factor_sat random'
            min_value_opt = '--min-value {0}'.format(self.min_value)
            max_value_arg = str(self.max_value)
            seed_opt = '--seed {0}'.format(self.seed) if self.seed else ''
            number_type_opt = fold_number_type(
                self.number.number_type,
                f_prime='--prime',
                f_prob_prime='--prime --error {0}'.format,
                f_comp='--no-prime',
                f_prob_comp='--no-prime --error {0}'.format,
                f_unknown=''
            )

            reproduce = ' '.join(filter(bool, [command, min_value_opt, seed_opt, number_type_opt, max_value_arg]))
        else:
            reproduce = 'gen_factor_sat number {0}'.format(self.number)

        comments.append('To reproduce this results call: ' + reproduce)
        comments.append('')

        number = 'Factorization of the number: {0}'.format(self.number)
        factor_1 = 'Factor 1 is encoded in the variables: {0}'.format(self.factor_1)
        factor_2 = 'Factor 2 is encoded in the variables: {0}'.format(self.factor_2)
        encoding = 'All numbers are encoded with [msb, ..., lsb]'
        comments.extend([number, factor_1, factor_2, encoding])

        return cnf_to_dimacs(self.number_of_variables, self.clauses, comments=comments)


def factorize_random_number(
        max_value: int,
        min_value: int = 2,
        seed: Optional[int] = None,
        number_type: Optional[NumberType] = None,
        max_tries: int = 1000) -> FactoringSat:
    if seed is None:
        seed = random.randrange(sys.maxsize)

    number = generate_number(
        max_value=max_value,
        min_value=min_value,
        seed=seed,
        max_tries=max_tries,
        number_type=number_type
    )

    factor_sat = factorize_number(number)
    factor_sat.seed = seed
    factor_sat.max_value = max_value
    factor_sat.min_value = min_value

    return factor_sat


def factorize_number(number: Number) -> FactoringSat:
    cnf_builder = CNFBuilder()
    factoring_circuit = TseitinFactoringStrategy()

    bin_number = utils.to_bin_list(number.value)
    factor_length_1, factor_length_2 = _factor_lengths(len(bin_number))

    factor_1 = cnf_builder.next_variables(factor_length_1)
    factor_2 = cnf_builder.next_variables(factor_length_2)

    fact_result = factoring_circuit.factorize(
        cast(List[Symbol], factor_1),
        cast(List[Symbol], factor_2),
        cast(List[Symbol], bin_number),
        cnf_builder
    )

    factoring_circuit.assume(fact_result, factoring_circuit.one, cnf_builder)

    return FactoringSat(
        number=number,
        factor_1=factor_1,
        factor_2=factor_2,
        number_of_variables=cnf_builder.number_of_variables,
        clauses=cnf_builder.build_clauses()
    )


def _factor_lengths(number_length: int) -> Tuple[int, int]:
    factor_length_1 = math.ceil(number_length / 2)
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
