from __future__ import annotations

import functools
import itertools
import math
from abc import ABC
from dataclasses import dataclass
from random import Random
from typing import Optional


@dataclass()
class GeneratorConfig:
    min_value: int
    max_value: int
    seed: int

    @staticmethod
    def create(min_value: int, max_value: int, seed: int) -> GeneratorConfig:
        if min_value < 2:
            raise ValueError('The minimum value must be greater than or equal to 2')

        if max_value < min_value:
            raise ValueError('The maximum value must be greater than or equal to the minimum value')

        return GeneratorConfig(min_value, max_value, seed)

    @staticmethod
    def generator(generator_config: GeneratorConfig):
        rand = Random(generator_config.seed)
        while True:
            yield rand.randint(generator_config.min_value, generator_config.max_value)


@dataclass()
class Number(ABC):
    value: int

    @staticmethod
    def unchecked(value: int) -> Number:
        """
        Create a number without determining its type.

        :param value: the value of the number
        :return: the number
        """
        return Unknown(value)

    @staticmethod
    def create(value: int, seed: int, error: float) -> Number:
        """
        Create a number of the corresponding type. If a small error rate is
        allowed, a probabilistic (seeded) prime test is used. In this case,
        the resulting number is marked as probabilistic.

        :param value: the value of the number
        :param seed: the seed for the probabilistic prime test
        :param error: the max error probability
        :return: the number
        """
        if error > 0.0:
            if is_prob_prime(value, error, seed):
                return ProbPrime(value, error)
            else:
                return ProbComposite(value=value, error=error)
        else:
            if is_prime(value):
                return DetPrime(value)
            else:
                return DetComposite(value)

    @staticmethod
    def generate(
            generator_config: GeneratorConfig,
            prime: Optional[bool] = None,
            error: float = 0.0,
            max_tries: int = 1000) -> Number:
        """
        Generate a number based on the specified generator configuration.
        The optional prime flag can be used to specify whether the resulting
        number should be a prime or composite number. If a small error rate
        is allowed, a probabilistic prime test is used. Stops if no number with
        the correct type can be found within the given number of tries.

        :param generator_config: the configuration to generate number candidates
        :param prime: whether the number should be a prime number
        :param error: the permitted error probability
        :param max_tries: the number of tries to generate a number
        :return: the generated number
        """
        generator = GeneratorConfig.generator(generator_config)

        try:
            if prime is None:
                return next(map(Number.unchecked, generator))
            else:
                get_type = functools.partial(Number.create, error=error, seed=generator_config.seed)
                has_not_correct_type = functools.partial(Number.check_type, prime=not prime)
                numbers = map(get_type, itertools.islice(generator, max_tries))
                return next(itertools.dropwhile(has_not_correct_type, numbers))

        except StopIteration:
            if prime is None:
                number_type = "random"
            elif prime:
                number_type = "prime"
            else:
                number_type = "composite"

            raise StopIteration('Failed to generate a {0} number within {1} tries'.format(number_type, max_tries))

    @staticmethod
    def check_type(number: Number, prime: bool) -> bool:
        """
        Check whether the given number is of the specified type.

        :param number: the number to be checked
        :param prime: the type of the number
        :return: true if teh number is of the specified type, otherwise false
        """
        if prime:
            return isinstance(number, Prime)
        else:
            return isinstance(number, Composite)

    def fold(self: Number, f_det_prime, f_prob_prime, f_det_comp, f_prob_comp, f_unknown):
        if isinstance(self, DetPrime):
            return f_det_prime(self.value)
        elif isinstance(self, ProbPrime):
            return f_prob_prime(self.value, self.error)
        elif isinstance(self, DetComposite):
            return f_det_comp(self.value)
        elif isinstance(self, ProbComposite):
            return f_prob_comp(self.value, self.error)
        elif isinstance(self, Unknown):
            return f_unknown(self)
        else:
            raise ValueError('Unknown number type: ' + str(self))

    def fold_type(self: Number, v_det_prime, v_prob_prime, v_det_comp, v_prob_comp, v_unknown):
        return self.fold(
            f_det_prime=lambda value: v_det_prime,
            f_prob_prime=lambda value, error: v_prob_prime,
            f_det_comp=lambda value: v_det_comp,
            f_prob_comp=lambda value, error: v_prob_comp,
            f_unknown=lambda value: v_unknown
        )

    def fold_error_type(self: Number, v_det_prime, f_prob_prime, v_det_comp, f_prob_comp, v_unknown):
        return self.fold(
            f_det_prime=lambda value: v_det_prime,
            f_prob_prime=lambda value, error: f_prob_prime(error),
            f_det_comp=lambda value: v_det_comp,
            f_prob_comp=lambda value, error: f_prob_comp(error),
            f_unknown=lambda value: v_unknown
        )


@dataclass()
class Prime(Number, ABC):
    pass


@dataclass()
class DetPrime(Prime):
    pass


@dataclass()
class ProbPrime(Prime):
    error: float


@dataclass()
class Composite(Number, ABC):
    pass


@dataclass()
class ProbComposite(Composite):
    error: float


@dataclass()
class DetComposite(Composite):
    pass


@dataclass()
class Unknown(Number):
    pass


def is_prime(value: int):
    if value == 2:
        return True
    else:
        return all(value % x != 0 for x in range(2, math.ceil(math.sqrt(value)) + 1))


def is_prob_prime(value: int, error: float, seed: int):
    rand = Random(seed)

    iterations = math.ceil(-math.log(error) / math.log(4))
    for iteration in range(0, iterations):
        a = rand.randrange(1, value)
        if not _miller_rabin(value, a):
            return False

    return True


def _miller_rabin(number: int, a: int):
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
