from abc import ABC, abstractmethod
from typing import List, Generic, TypeVar

T = TypeVar('T')
W = TypeVar('W')


class MultiplicationStrategy(Generic[T, W], ABC):

    @abstractmethod
    def multiply(self, factor_1: List[T], factor_2: List[T], writer: W) -> List[T]:
        pass