from __future__ import annotations

import math
import random
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple, cast

from gen_factor_sat import utils
from gen_factor_sat.circuit.instances import FactoringAndGateStrategy, TseitinFactoringStrategy
from gen_factor_sat.formula.cnf import CNF, CNFBuilder
from gen_factor_sat.formula.symbol import Symbol, Variable
from gen_factor_sat.number_generator import Number, GeneratorConfig

SymFacStrategy = FactoringAndGateStrategy[Symbol, CNFBuilder]


@dataclass
class FactoringSat:
    """
    This data class provides all relevant information about the transformation of
    the factoring problem into SAT. Besides the resulting CNF, this includes the
    variables encoding the factors and all necessary configurations to reproduce
    the results.
    """
    VERSION = '0.3'
    number: Number
    factor_1: List[Variable]
    factor_2: List[Variable]
    cnf: CNF
    generator: Optional[GeneratorConfig] = None

    @staticmethod
    def __default_strategy() -> SymFacStrategy:
        return TseitinFactoringStrategy()

    @staticmethod
    def factorize_random_number(
            max_value: int,
            min_value: int = 2,
            seed: Optional[int] = None,
            prime: Optional[bool] = None,
            error: float = 0.0,
            max_tries: int = 1000,
            strategy: Optional[SymFacStrategy] = None
    ) -> FactoringSat:
        """
        Encode the factoring of a pseudo-randomly generated number into a CNF.
        The number generator as well as the encoding is deterministic. Therefore,
        calling this function with the same configuration produces the same result.

        The optional prime flag can be used to specify whether the resulting
        number should be a prime or composite number. If a small error rate
        is allowed, a probabilistic prime test is used. Stops if no number with
        the correct type can be found within the given number of tries.
        See the number generator module for more details.

        :param max_value: the largest possible value the generated number can have
        :param min_value: the smallest possible value the generated number can have
        :param seed: the seed used to generate the number
        :param prime: whether the number should be a prime number
        :param error: the permitted error probability
        :param max_tries: the number of tries to generate a number
        :param strategy: the strategy to be used
        :return: the encoded factoring instance (see FactoringSat)
        """
        if seed is None:
            seed = random.randrange(sys.maxsize)

        generator_config = GeneratorConfig.create(min_value, max_value, seed)
        number = Number.generate(
            generator_config=generator_config,
            prime=prime,
            error=error,
            max_tries=max_tries
        )

        factor_sat = FactoringSat.__factorize_number(number, strategy)
        factor_sat.generator = generator_config

        return factor_sat

    @staticmethod
    def factorize_number(
            number: int,
            strategy: Optional[SymFacStrategy] = None
    ) -> FactoringSat:
        """
        Encode the factoring of the specified number into a CNF.
        The encoding is deterministic. Therefore, calling this method with the
        same number produces the same result.

        :param number: the number to be factorized
        :param strategy: the strategy to be used
        :return: the encoded factoring instance (see FactoringSat)
        """
        return FactoringSat.__factorize_number(Number.unchecked(number), strategy)

    @staticmethod
    def __factorize_number(number: Number, strategy: Optional[SymFacStrategy] = None) -> FactoringSat:
        if strategy is None:
            strategy = FactoringSat.__default_strategy()

        cnf_builder = CNFBuilder()

        bin_number = utils.to_bin_list(number.value)
        factor_length_1, factor_length_2 = FactoringSat.__factor_lengths(len(bin_number))

        factor_1 = cnf_builder.next_variables(factor_length_1)
        factor_2 = cnf_builder.next_variables(factor_length_2)

        fact_result = strategy.is_factorization(
            cast(List[Symbol], factor_1),
            cast(List[Symbol], factor_2),
            cast(List[Symbol], bin_number),
            cnf_builder
        )

        strategy.expect_one(fact_result, cnf_builder)

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

    def to_dimacs(self) -> str:
        """
        Encode this factoring instance into DIMACS. The comments includes
        instructions to reproduce these results and the variables encoding
        the factors.

        :return: the resulting DIMACS
        """
        comments = []
        comments.append('GenFactorSat v{0}'.format(FactoringSat.VERSION))

        if self.generator:
            interval = '[{0}, {1}]'.format(self.generator.min_value, self.generator.max_value)
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

        reproduce = self.reproduce_command()
        comments.append('To reproduce this results call: ' + reproduce)
        comments.append('')

        number = 'Factorization of the number: {0}'.format(self.number.value)
        factor_1 = 'Factor 1 is encoded in the variables: {0}'.format(self.factor_1)
        factor_2 = 'Factor 2 is encoded in the variables: {0}'.format(self.factor_2)
        encoding = 'All numbers are encoded with [msb, ..., lsb]'
        comments.extend([number, factor_1, factor_2, encoding])

        return self.cnf.to_dimacs(comments=comments)

    def reproduce_command(self) -> str:
        """
        Generate a command to reproduce this results.

        :return: the command
        """
        if self.generator:
            command = 'gen_factor_sat random'
            seed_opt = '--seed {0}'.format(self.generator.seed)
            min_value_opt = '--min-value {0}'.format(self.generator.min_value)
            max_value_arg = str(self.generator.max_value)
            number_type_opt = self.number.fold_error_type(
                v_det_prime='--prime',
                f_prob_prime='--prime --error {0}'.format,
                v_det_comp='--no-prime',
                f_prob_comp='--no-prime --error {0}'.format,
                v_unknown=None
            )

            return ' '.join(filter(bool, [command, number_type_opt, seed_opt, min_value_opt, max_value_arg]))
        else:
            return 'gen_factor_sat number {0}'.format(self.number.value)
