import itertools
import math
from dataclasses import dataclass
from enum import Enum
from random import Random
from typing import Union, Optional


class NumberBaseType(Enum):
    PRIME = 'prime'
    COMPOSITE = 'composite'
    UNKNOWN = 'random'


@dataclass()
class ProbableCheck:
    error: float


@dataclass()
class DeterministicCheck:
    pass


NumberCheckType = Union[DeterministicCheck, ProbableCheck, None]


@dataclass()
class NumberType:
    number_base_type: NumberBaseType
    number_check_type: NumberCheckType


@dataclass()
class Number:
    value: int
    number_type: NumberType


def fold_number_type(number_type: NumberType, f_prime, f_prob_prime, f_comp, f_prob_comp, f_unknown):
    if number_type.number_base_type == NumberBaseType.PRIME:
        if isinstance(number_type.number_check_type, DeterministicCheck):
            return f_prime
        else:
            return f_prob_prime(number_type.number_check_type.error)

    elif number_type.number_base_type == NumberBaseType.COMPOSITE:
        if isinstance(number_type.number_check_type, DeterministicCheck):
            return f_comp
        else:
            return f_prob_comp(number_type.number_check_type.error)
    else:
        return f_unknown


def create_number(value: int, number_check: NumberCheckType, seed: int) -> Number:
    number_type = get_number_type(value, number_check, seed)
    return Number(value, number_type)


def get_number_type(value: int, number_check: NumberCheckType, seed: int):
    if isinstance(number_check, DeterministicCheck):
        prime_test_result = is_det_prime(value)
    elif isinstance(number_check, ProbableCheck):
        prime_test_result = is_prob_prime(value, seed, number_check.error)
    else:
        return NumberType(NumberBaseType.UNKOWN, number_check)

    number_base_type = NumberBaseType.PRIME if prime_test_result else NumberBaseType.COMPOSITE
    return NumberType(number_base_type, number_check)


def create_number_type(prime: Optional[bool] = None, error: Optional[float] = None):
    base_type = create_number_base_type(prime)
    check_type = create_number_check(error)
    return NumberType(base_type, check_type)


def create_number_check(error: Optional[float] = None) -> NumberCheckType:
    if (error is None) or (error <= 0.0):
        return DeterministicCheck()
    else:
        return ProbableCheck(error)


def create_number_base_type(prime: Optional[bool]) -> NumberBaseType:
    if prime is None:
        return NumberBaseType.UNKNOWN
    elif prime:
        return NumberBaseType.PRIME
    else:
        return NumberBaseType.COMPOSITE


def generate_number(
        max_value: int,
        min_value: int,
        seed: int,
        number_type: Optional[NumberType] = None,
        max_tries: int = 100) -> Number:
    if number_type is None:
        number_type = NumberType(NumberBaseType.UNKNOWN, None)

    generator = number_generator(min_value, max_value, seed, number_type.number_check_type)

    def has_not_correct_type(number: Number) -> bool:
        return (number.number_type != number_type) and (number_type.number_base_type != NumberBaseType.UNKNOWN)

    try:
        return next(itertools.dropwhile(has_not_correct_type, itertools.islice(generator, max_tries)))
    except StopIteration:
        raise ValueError(
            'Failed to generate a {0} number within {1} tries'.format(number_type.number_base_type.value, max_tries))


def number_generator(min_value: int, max_value: int, seed: int, number_check: NumberCheckType):
    rand = Random(seed)
    while True:
        yield create_number(rand.randint(min_value, max_value), number_check, seed)


def is_det_prime(value: int):
    if value == 2:
        return True
    else:
        return all(value % x != 0 for x in range(2, math.ceil(math.sqrt(value)) + 1))


def is_prob_prime(value: int, error: float, seed: int):
    rand = Random(seed)

    iterations = math.ceil(-math.log(error) / math.log(4))
    for iteration in range(0, iterations):
        a = rand.randrange(1, value)
        if not miller_rabin(value, a):
            return False

    return True


def miller_rabin(number: int, a: int):
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
