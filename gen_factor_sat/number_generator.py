import functools
import itertools
import math
from abc import ABC
from dataclasses import dataclass
from random import Random
from typing import Optional
from gen_factor_sat import utils

@dataclass()
class Number(ABC):
    value: int


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


def create_number(value: int, seed: int, error: float) -> Number:
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


def check_type(number: Number, prime: bool) -> bool:
    if prime:
        return isinstance(number, Prime)
    else:
        return isinstance(number, Composite)


def fold_number(number: Number, f_det_prime, f_prob_prime, f_det_comp, f_prob_comp, f_unknown):
    if isinstance(number, DetPrime):
        return f_det_prime(number.value)
    elif isinstance(number, ProbPrime):
        return f_prob_prime(number.value, number.error)
    elif isinstance(number, DetComposite):
        return f_det_comp(number.value)
    elif isinstance(number, ProbComposite):
        return f_prob_comp(number.value, number.error)
    elif isinstance(number, Unknown):
        return f_unknown(number)
    else:
        raise ValueError('Unknown number type: ' + str(number))


def fold_number_type(number: Number, v_det_prime, v_prob_prime, v_det_comp, v_prob_comp, v_unknown):
    return fold_number(
        number,
        f_det_prime=lambda value: v_det_prime,
        f_prob_prime=lambda value, error: v_prob_prime,
        f_det_comp=lambda value: v_det_comp,
        f_prob_comp=lambda value, error: v_prob_comp,
        f_unknown=lambda value: v_unknown
    )


def fold_number_prob_type(number: Number, v_det_prime, f_prob_prime, v_det_comp, f_prob_comp, v_unknown):
    return fold_number(
        number,
        f_det_prime=lambda value: v_det_prime,
        f_prob_prime=lambda value, error: f_prob_prime(error),
        f_det_comp=lambda value: v_det_comp,
        f_prob_comp=lambda value, error: f_prob_comp(error),
        f_unknown=lambda value: v_unknown
    )

def generate_number(
        max_value: int,
        min_value: int,
        seed: int,
        prime: Optional[bool] = None,
        error: float = 0.0,
        max_tries: int = 100) -> Number:
    generator = number_generator(min_value, max_value, seed)

    try:
        if prime is None:
            return next(map(Unknown, generator))
        else:
            get_type = functools.partial(create_number, error=error, seed=seed)
            has_not_correct_type = functools.partial(check_type, prime=not prime)
            numbers = map(get_type, itertools.islice(generator, max_tries))
            return next(itertools.dropwhile(has_not_correct_type, numbers))

    except StopIteration:
        if prime is None:
            number_type = "random"
        elif prime:
            number_type = "prime"
        else:
            number_type = "composite"

        raise ValueError('Failed to generate a {0} number within {1} tries'.format(number_type, max_tries))


def number_generator(min_value: int, max_value: int, seed: int):
    rand = Random(seed)
    while True:
        yield rand.randint(min_value, max_value)


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
