import math
import random
import sys
from dataclasses import dataclass
from random import Random
from typing import List, Set, Optional, Tuple, cast

from gen_factor_sat import utils
from gen_factor_sat.circuit.instances import TseitinFactoringStrategy
from gen_factor_sat.circuit.tseitin.circuit import CNFBuilder
from gen_factor_sat.circuit.tseitin.encoding import Clause, Symbol, Variable

VERSION = '0.3'


@dataclass
class FactoringSat:
    number: int
    factor_1: List[Variable]
    factor_2: List[Variable]
    number_of_variables: int
    clauses: Set[Clause]
    max_value: Optional[int] = None
    min_value: Optional[int] = None
    seed: Optional[int] = None
    prime: Optional[bool] = None
    error: float = 0.0

    def to_dimacs(self):
        comments = []
        comments.append('GenFactorSat v{0}'.format(VERSION))

        if self.max_value:
            interval = '[{0}, {1}]'.format(self.min_value, self.max_value)
            comments.append('The number was (pseudo-) randomly chosen from the interval: ' + interval)

            if self.prime is not None:
                if self.prime and self.error > 0.0:
                    number_type = 'The number is a prime number with an error probability less or equal to {0}.'\
                        .format(self.error)
                elif self.prime and self.error <= 0.0:
                    number_type = 'The number is a prime number.'
                else:
                    number_type = 'The number is a composite number.'

                comments.append(number_type)


            command = 'gen_factor_sat random'
            min_value_opt = '--min-value {0}'.format(self.min_value)
            seed_opt = '--seed {0}'.format(self.seed) if self.seed else ''
            if self.prime is not None:
                prime_opt = '--prime' if self.prime else '--no-prime'
                error_opt = '--error {0}'.format(self.error) if self.error > 0.0 else ''
            else:
                prime_opt = ''
                error_opt = ''

            max_value_arg = str(self.max_value)

            reproduce = ' '.join(filter(bool, [command, min_value_opt, seed_opt, prime_opt, error_opt, max_value_arg]))
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


def factorize_random_number(max_value: int, min_value: int = 2, seed: Optional[int] = None,
                            prime: Optional[bool] = None,
                            error=0.0) -> FactoringSat:
    if seed is None:
        seed = random.randrange(sys.maxsize)

    number = _generate_number(max_value=max_value, min_value=min_value, seed=seed, prime=prime, error=error)
    factor_sat = factorize_number(number)
    factor_sat.seed = seed
    factor_sat.max_value = max_value
    factor_sat.min_value = min_value
    factor_sat.prime = prime
    factor_sat.error = error

    return factor_sat


def factorize_number(number: int) -> FactoringSat:
    cnf_builder = CNFBuilder()
    factoring_circuit = TseitinFactoringStrategy()

    bin_number = utils.to_bin_list(number)
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


def _generate_number(
        max_value: int,
        min_value: int,
        seed: int,
        prime: Optional[bool] = None,
        error: Optional[float] = None,
        max_tries: int = 100) -> int:
    rand = Random(seed)

    number = 0
    prime_check = None
    iteration = 0
    while number < 2 or prime != prime_check:
        iteration += 1
        if iteration > max_tries:
            raise ValueError("Cannot find a satisfying assignment within {0} tries".format(max_tries))

        number = rand.randint(min_value, max_value)

        if prime is not None:
            if error is None or error <= 0.0:
                prime_check = is_prime(number)
            else:
                prime_check = is_prob_prime(number, error, seed)

    return number


def is_prime(number):
    if number == 2:
        return True
    else:
        return all(number % x != 0 for x in range(2, math.ceil(math.sqrt(number)) + 1))


def is_prob_prime(number, error, seed):
    rand = Random(seed)

    iterations = math.ceil(-math.log(error) / math.log(4))
    for iteration in range(0, iterations):
        a = rand.randrange(1, number)
        if not miller_rabin(number, a):
            return False

    return True


def miller_rabin(number, a):
    d = 1
    dd = 1

    for b in bin(number - 1)[2:]:
        d = d * d % number
        if d == 1 and dd != 1 and dd != number - 1:
            return False

        if b == '1':
            d = d * a % number

        dd = d

    return d == 1


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
