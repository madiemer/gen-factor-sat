from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass
from typing import List, Set, Optional, Tuple, cast

from gen_factor_sat import utils
from gen_factor_sat.circuit.instances import TseitinFactoringStrategy
from gen_factor_sat.circuit.tseitin.circuit import CNFBuilder
from gen_factor_sat.formula.cnf import Clause, CNF
from gen_factor_sat.formula.symbol import Symbol, Variable
from gen_factor_sat.number_generator import Number


@dataclass
class FactoringSat:
    VERSION = '0.3'
    number: Number
    factor_1: List[Variable]
    factor_2: List[Variable]
    cnf: CNF
    max_value: Optional[int] = None
    min_value: Optional[int] = None
    seed: Optional[int] = None

    def to_dimacs(self):
        comments = []
        comments.append('GenFactorSat v{0}'.format(FactoringSat.VERSION))

        if self.max_value:
            interval = '[{0}, {1}]'.format(self.min_value, self.max_value)
            comments.append('The number was (pseudo-) randomly chosen from the interval: ' + interval)

            number_type = self.number.fold_error_type(
                v_det_prime='The number is a prime number.',
                f_prob_prime='The number is a prime number with an error probability less or equal to {0}.'.format,
                v_det_comp='The number is a composite number.',
                f_prob_comp=lambda error: 'The number is a composite number.',
                v_unknown=None
            )

            if number_type:
                comments.append(number_type)

            command = 'gen_factor_sat random'
            min_value_opt = '--min-value {0}'.format(self.min_value)
            max_value_arg = str(self.max_value)
            seed_opt = '--seed {0}'.format(self.seed) if self.seed else ''
            number_type_opt = self.number.fold_error_type(
                v_det_prime='--prime',
                f_prob_prime='--prime --error {0}'.format,
                v_det_comp='--no-prime',
                f_prob_comp='--no-prime --error {0}'.format,
                v_unknown=None
            )

            reproduce = ' '.join(filter(bool, [command, min_value_opt, seed_opt, number_type_opt, max_value_arg]))
        else:
            reproduce = 'gen_factor_sat number {0}'.format(self.number)

        comments.append('To reproduce this results call: ' + reproduce)
        comments.append('')

        number = 'Factorization of the number: {0}'.format(self.number.value)
        factor_1 = 'Factor 1 is encoded in the variables: {0}'.format(self.factor_1)
        factor_2 = 'Factor 2 is encoded in the variables: {0}'.format(self.factor_2)
        encoding = 'All numbers are encoded with [msb, ..., lsb]'
        comments.extend([number, factor_1, factor_2, encoding])

        return self.cnf.to_dimacs(comments=comments)

    @staticmethod
    def factorize_random_number(
            max_value: int,
            min_value: int = 2,
            seed: Optional[int] = None,
            prime: Optional[bool] = None,
            error: float = 0.0,
            max_tries: int = 1000) -> FactoringSat:
        if seed is None:
            seed = random.randrange(sys.maxsize)

        number = Number.generate(
            max_value=max_value,
            min_value=min_value,
            seed=seed,
            prime=prime,
            error=error,
            max_tries=max_tries
        )

        factor_sat = FactoringSat.factorize_number(number)
        factor_sat.seed = seed
        factor_sat.max_value = max_value
        factor_sat.min_value = min_value

        return factor_sat

    @staticmethod
    def factorize_number(number: Number) -> FactoringSat:
        cnf_builder = CNFBuilder()
        factoring_circuit = TseitinFactoringStrategy()

        bin_number = utils.to_bin_list(number.value)
        factor_length_1, factor_length_2 = FactoringSat.__factor_lengths(len(bin_number))

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
            cnf=cnf_builder.build()
        )

    @staticmethod
    def __factor_lengths(number_length: int) -> Tuple[int, int]:
        factor_length_1 = math.ceil(number_length / 2)
        factor_length_2 = number_length - 1

        return factor_length_1, factor_length_2