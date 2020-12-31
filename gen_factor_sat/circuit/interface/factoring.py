"""
Factoring

Interfaces for factorizing numbers.
"""

from abc import ABC, abstractmethod
from typing import List, Generic, TypeVar

T = TypeVar('T')
W = TypeVar('W')


class FactoringStrategy(Generic[T, W], ABC):
    """
    The evaluation strategy for factoring numbers.
    """

    @abstractmethod
    def is_factorization(self, factor_1: List[T], factor_2: List[T], number: List[T], writer: W) -> T:
        """
        Check whether the factors are a valid factorization of the given number.
        A factoring is valid if the product of the factors result int the
        specified number.

        :param factor_1: the first factor
        :param factor_2: the second factor
        :param number: the number to be factorized
        :param writer: a writer for stateful operations
        :return: one if the factors are a valid factorization, otherwise zero
        """
        pass
