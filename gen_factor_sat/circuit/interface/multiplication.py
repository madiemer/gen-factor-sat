"""
Multiplication

Interfaces for multiplication strategies.
"""
from abc import ABC, abstractmethod
from typing import List, Generic, TypeVar

T = TypeVar('T')
W = TypeVar('W')


class MultiplicationStrategy(Generic[T, W], ABC):
    """
    The evaluation strategy for multiplications.
    """

    @abstractmethod
    def multiply(self, factor_1: List[T], factor_2: List[T], writer: W) -> List[T]:
        """
        Calculate the product of both factors.

        :param factor_1: the first factor
        :param factor_2: the second factor
        :param writer: a writer for stateful operations
        :return: the product of the factors
        """
        pass
